#!/usr/bin/env node
/**
 * OMX-side interop worker (Codex lane).
 *
 * Reads the oldest pending omc->omx task from interop shared-state, runs the
 * real Codex model on it via `omx-api exec`, and writes the model's answer
 * back into shared-state as the task result (status=completed), or records an
 * error (status=failed).
 *
 * Usage:
 *   node omx-interop-worker.mjs <cwd> [timeoutSec]
 */
import { spawnSync } from 'child_process';

const MOD =
  '/Users/liuchengxu/.nvm/versions/node/v24.18.0/lib/node_modules/oh-my-claude-sisyphus/dist';
const { readSharedTasks, updateSharedTask } = await import(
  `file://${MOD}/interop/shared-state.js`
);

const [, , cwd, timeoutSecRaw] = process.argv;
const timeoutSec = timeoutSecRaw ? Number(timeoutSecRaw) : 200;

function pickPendingTask() {
  // shared-state returns newest first; take the oldest pending omc->omx task.
  const tasks = readSharedTasks(cwd, { source: 'omc', target: 'omx', status: 'pending' });
  return tasks.length ? tasks[tasks.length - 1] : null;
}

const task = pickPendingTask();
if (!task) {
  console.error('[omx] no pending omc->omx task found');
  process.exit(4);
}

console.log(`[omx] picked task ${task.id}`);
updateSharedTask(cwd, task.id, { status: 'in_progress' });

// Run the real Codex model on the task description via the API-relay lane.
const prompt =
  'You are the OMX (Codex) worker in an OMC<->OMX interop proof. ' +
  'Answer the following task concisely and concretely. Task:\n\n' +
  task.description;

const res = spawnSync('/Users/liuchengxu/.local/bin/omx-api', ['exec', '-C', cwd, '-'], {
  input: prompt,
  encoding: 'utf-8',
  timeout: timeoutSec * 1000,
  maxBuffer: 20 * 1024 * 1024,
});

if (res.status !== 0 || res.error) {
  const err = res.error ? String(res.error) : `exit ${res.status}`;
  updateSharedTask(cwd, task.id, {
    status: 'failed',
    error: `omx-api exec failed: ${err}`,
  });
  console.error(`[omx] task ${task.id} failed: ${err}`);
  if (res.stderr) console.error(res.stderr.slice(-2000));
  process.exit(5);
}

const out = (res.stdout || '').trim();
updateSharedTask(cwd, task.id, {
  status: 'completed',
  result: out,
});
console.log(`[omx] task ${task.id} completed, ${out.length} chars`);
process.exit(0);

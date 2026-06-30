#!/usr/bin/env node
/**
 * OMC-side interop driver (Claude lane = leader).
 *
 * Step 1 (place): OMC initializes the interop session and posts a real task
 *   targeted at OMX (Codex lane).
 * Step 2 (collect): OMC polls shared-state until OMX marks the task completed
 *   (or failed / timeout), then prints the result and a verdict.
 *
 * Usage:
 *   node omc-interop-driver.mjs place   <cwd> <sessionId> <taskFile>
 *   node omc-interop-driver.mjs collect <cwd> <taskId> [timeoutMs]
 */
import { readFileSync } from 'fs';

const MOD =
  '/Users/liuchengxu/.nvm/versions/node/v24.18.0/lib/node_modules/oh-my-claude-sisyphus/dist';
const {
  initInteropSession,
  addSharedTask,
  readSharedTasks,
  updateSharedTask,
} = await import(`file://${MOD}/interop/shared-state.js`);

const [, , action, cwd, a3, a4] = process.argv;

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

if (action === 'place') {
  const sessionId = a3;
  const taskFile = a4;
  const description = readFileSync(taskFile, 'utf-8');
  initInteropSession(sessionId, cwd, cwd);
  const task = addSharedTask(cwd, {
    source: 'omc',
    target: 'omx',
    type: 'analyze',
    description,
    files: [],
  });
  // Print only the task id on stdout so the shell can capture it.
  process.stdout.write(task.id + '\n');
  process.exit(0);
}

if (action === 'collect') {
  const taskId = a3;
  const timeoutMs = a4 ? Number(a4) : 240000;
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const tasks = readSharedTasks(cwd);
    const task = tasks.find((t) => t.id === taskId);
    if (task && (task.status === 'completed' || task.status === 'failed')) {
      console.log(JSON.stringify({
        id: task.id,
        status: task.status,
        result: task.result ?? null,
        resultArtifact: task.resultArtifact ?? null,
        error: task.error ?? null,
        completedAt: task.completedAt ?? null,
      }, null, 2));
      process.exit(task.status === 'completed' ? 0 : 2);
    }
    await sleep(2000);
  }
  console.error(`[omc] timeout waiting for task ${taskId}`);
  process.exit(3);
}

console.error(`unknown action: ${action}`);
process.exit(64);

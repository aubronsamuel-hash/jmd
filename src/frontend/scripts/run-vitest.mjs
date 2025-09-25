#!/usr/bin/env node
import { spawn } from 'node:child_process';

const rawArgs = process.argv.slice(2);
const filteredArgs = [];
let runInBandRequested = false;

for (const arg of rawArgs) {
  if (arg === '--runInBand' || arg === '--run-in-band') {
    runInBandRequested = true;
    continue;
  }
  filteredArgs.push(arg);
}

const vitestArgs = [...filteredArgs];

if (runInBandRequested) {
  const firstArg = vitestArgs[0];
  const hasExplicitCommand = Boolean(firstArg && !firstArg.startsWith('-'));

  if (!hasExplicitCommand) {
    vitestArgs.unshift('run');
  }

  vitestArgs.push('--pool=threads', '--maxWorkers=1', '--minWorkers=1', '--no-file-parallelism');
}

const child = spawn('vitest', vitestArgs, {
  stdio: 'inherit',
  shell: process.platform === 'win32',
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});

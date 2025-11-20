#!/usr/bin/env bun
import { spawn } from 'node:child_process';

// Proxy CLI to Python entrypoint defined in pyproject [project.scripts]
// Tries `uv run --quiet python -m pypjt` first; falls back to `python -m pypjt`.

const args: string[] = process.argv.slice(2);

function run(command: string, commandArgs: string[]): Promise<number> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, commandArgs, {
      stdio: 'inherit',
      env: process.env,
    });
    child.on('close', (code) => resolve(code ?? 1));
    child.on('error', (error: unknown) => reject(error));
  });
}

async function main(): Promise<void> {
    const code = await run('python3', ['-m', 'pypjt.create', ...args]);
    process.exit(code);
}

main().catch(() => process.exit(1));

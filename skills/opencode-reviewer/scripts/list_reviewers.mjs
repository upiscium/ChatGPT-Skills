#!/usr/bin/env node
// Read-only inspection; compatible with Node and Bun. Never launches a review.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { isAbsolute } from 'node:path';
import { realpathSync, statSync } from 'node:fs';

const [directory, ...requested] = process.argv.slice(2);
const emit = value => process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
const fail = (status, details = {}) => {
  emit({ status, ...details });
  process.exit(2);
};
if (!directory || !isAbsolute(directory) || requested.some(x => x.startsWith('-'))) {
  fail('usage', { usage: 'node|bun list_reviewers.mjs <absolute-review-directory> [exact-role ...]' });
}
let cwd;
try {
  cwd = realpathSync(directory);
  if (!statSync(cwd).isDirectory()) fail('not-a-directory');
} catch {
  fail('directory-unavailable');
}
const command = args => execFileSync('opencode', args, {
  cwd, encoding: 'utf8', timeout: 20000, maxBuffer: 16 * 1024 * 1024,
  stdio: ['ignore', 'pipe', 'pipe'],
});
let version, output;
try {
  version = command(['--version']).trim();
  output = command(['agent', 'list']).replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, '');
} catch {
  fail('agent-list-failed', { directory: cwd, action: 'Inspect the native command error privately in the same environment.' });
}
// Some versions print ]reviewer (subagent) without a newline after permissions.
const roles = [...output.matchAll(/([A-Za-z0-9][A-Za-z0-9_./-]*)\s+\((primary|subagent|all)\)/g)]
  .map(match => ({ name: match[1], mode: match[2] }));
if (!roles.length || new Set(roles.map(x => x.name)).size !== roles.length) {
  fail('listing-format-unsupported', { version, directory: cwd, action: 'Inspect complete native output or the supported structured agent API; absence is unproven.' });
}
const missing = requested.filter(name => !roles.some(role => role.name === name));
if (missing.length) fail('requested-role-not-listed', { version, directory: cwd, missing, listed_roles: roles });
const candidates = requested.length ? requested : roles.filter(role => /review|audit|security/i.test(role.name)).map(role => role.name);
const inspected = [];
for (const name of candidates) {
  let agent;
  try {
    agent = JSON.parse(command(['debug', 'agent', name]));
  } catch {
    fail('role-metadata-unavailable', { version, directory: cwd, role: name, listed_roles: roles });
  }
  if (agent.name !== name || agent.mode !== roles.find(role => role.name === name).mode || !Array.isArray(agent.permission)) {
    fail('role-metadata-mismatch', { version, directory: cwd, role: name });
  }
  const permissions = agent.permission;
  const fingerprint = createHash('sha256').update(JSON.stringify({
    name: agent.name, mode: agent.mode, description: agent.description,
    model: agent.model, variant: agent.variant, options: agent.options,
    prompt: agent.prompt, permission: permissions,
  })).digest('hex');
  inspected.push({
    name: agent.name, mode: agent.mode, description: agent.description ?? null,
    model: agent.model ?? null, variant: agent.variant ?? null,
    reasoning_effort: agent.options?.reasoningEffort ?? null,
    configuration_sha256: fingerprint,
    permission_overview: ['read', 'edit', 'bash', 'task', 'question', 'webfetch', 'websearch'].map(permission => {
      const rules = permissions.filter(rule => rule.permission === permission);
      return { permission, last_wildcard_rule: rules.filter(rule => rule.pattern === '*').at(-1)?.action ?? 'inherit', rule_count: rules.length };
    }),
  });
}
emit({
  status: inspected.length ? 'listed-and-inspected' : 'no-named-reviewer-candidate',
  version, directory: cwd, observed_at: new Date().toISOString(),
  listed_roles: roles, candidates: inspected,
  limitation: 'Name-based candidates and a permission summary only. Inspect full effective rules and role descriptions for the intended operation. This does not verify a running session or authorize launch.',
});

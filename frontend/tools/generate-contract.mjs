import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import openapiTS, { astToString } from 'openapi-typescript';
const url = new URL('../../backend/contracts/openapi.json', import.meta.url);
const source = await fs.readFile(url);
const output = '// Generated from backend/contracts/openapi.json. Do not edit.\n// SHA-256: ' + crypto.createHash('sha256').update(source).digest('hex') + '\n' + astToString(await openapiTS(url));
await fs.writeFile(new URL('../src/client/schema.d.ts', import.meta.url), output);
console.log('Generated TypeScript from the current backend contract.');

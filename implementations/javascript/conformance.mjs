import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { validateManifest } from "./validator.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const corpusRoot = path.join(root, "resoverse_commons/corpus");
const index = JSON.parse(fs.readFileSync(path.join(corpusRoot, "index.json"), "utf8"));
const failures = [];

for (const testCase of index.cases) {
  const manifest = JSON.parse(fs.readFileSync(path.join(corpusRoot, testCase.manifest), "utf8"));
  const receipt = validateManifest(manifest);
  if (receipt.status !== testCase.expectedStatus) {
    failures.push({id: testCase.id, reason: `STATUS_MISMATCH:${testCase.expectedStatus}:${receipt.status}`});
  }
  if (JSON.stringify(receipt.reasonCodes) !== JSON.stringify(testCase.expectedReasonCodes)) {
    failures.push({id: testCase.id, reason: "REASON_CODES_MISMATCH"});
  }
}

const result = {
  implementation: "javascript-experimental",
  corpusVersion: index.corpusVersion,
  status: failures.length === 0 ? "PASS" : "HOLD",
  declaredCases: index.cases.length,
  completedCases: index.cases.length,
  failures,
  executionAttempted: false,
  admissionAuthorized: false,
};
console.log(JSON.stringify(result, null, 2));
process.exitCode = failures.length === 0 ? 0 : 2;

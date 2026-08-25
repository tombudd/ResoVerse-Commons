import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { validateManifest } from "./validator.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const corpusRoot = path.resolve(root, "resoverse_commons/corpus");
const failures = [];
let corpusVersion = null;
let cases = [];
let completed = 0;

function failure(id, reason) {
  failures.push({id, reason});
}

function object(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function safeRelative(value) {
  return typeof value === "string"
    && value.trim() !== ""
    && !/[\\\\\x00-\x1f\x7f]/u.test(value)
    && value !== "."
    && !value.startsWith("./")
    && !value.endsWith("/")
    && !value.includes("//")
    && !path.posix.isAbsolute(value)
    && !/^[A-Za-z]:/u.test(value)
    && !value.split("/").includes("..")
    && path.posix.normalize(value) === value;
}

try {
  const index = JSON.parse(fs.readFileSync(path.join(corpusRoot, "index.json"), "utf8"));
  if (!object(index) || Object.keys(index).length !== 2 || !Object.hasOwn(index, "corpusVersion") || !Object.hasOwn(index, "cases")) {
    failure("corpus", "INVALID_CORPUS_FIELDS");
  } else {
    corpusVersion = index.corpusVersion === "1.0" ? index.corpusVersion : null;
    if (corpusVersion === null) failure("corpus", "UNSUPPORTED_CORPUS_VERSION");
    if (!Array.isArray(index.cases)) {
      failure("corpus", "INVALID_CORPUS_CASES");
    } else if (index.cases.length === 0) {
      failure("corpus", "MISSING_CORPUS_CASES");
    } else {
      cases = index.cases;
    }
  }
} catch (error) {
  failure("corpus", `CORPUS_READ_FAILED:${error.name}`);
}

const seenIds = new Set();
for (const [position, testCase] of cases.entries()) {
  const fallbackId = `case-${position}`;
  if (!object(testCase) || Object.keys(testCase).length !== 4
    || !["id", "manifest", "expectedStatus", "expectedReasonCodes"].every((key) => Object.hasOwn(testCase, key))) {
    failure(fallbackId, "INVALID_CASE_FIELDS");
    continue;
  }
  if (typeof testCase.id !== "string" || testCase.id === "") {
    failure(fallbackId, "INVALID_CASE_ID");
    continue;
  }
  if (seenIds.has(testCase.id)) {
    failure(testCase.id, "DUPLICATE_CASE_ID");
    continue;
  }
  seenIds.add(testCase.id);
  if (!safeRelative(testCase.manifest)) {
    failure(testCase.id, "UNSAFE_CASE_PATH");
    continue;
  }
  if (!["PASS", "HOLD"].includes(testCase.expectedStatus)) {
    failure(testCase.id, "INVALID_EXPECTED_STATUS");
    continue;
  }
  if (!Array.isArray(testCase.expectedReasonCodes)
    || !testCase.expectedReasonCodes.every((reason) => typeof reason === "string" && reason !== "")
    || JSON.stringify(testCase.expectedReasonCodes) !== JSON.stringify([...new Set(testCase.expectedReasonCodes)].sort())) {
    failure(testCase.id, "INVALID_EXPECTED_REASON_CODES");
    continue;
  }
  const declaredPath = path.resolve(corpusRoot, testCase.manifest);
  let manifestPath;
  try {
    manifestPath = fs.realpathSync(declaredPath);
  } catch {
    failure(testCase.id, "CASE_PATH_OUTSIDE_CORPUS");
    continue;
  }
  const relativeToCorpus = path.relative(corpusRoot, manifestPath);
  if (relativeToCorpus === "" || relativeToCorpus.startsWith(`..${path.sep}`) || path.isAbsolute(relativeToCorpus)) {
    failure(testCase.id, "CASE_PATH_OUTSIDE_CORPUS");
    continue;
  }
  try {
    if (!fs.statSync(manifestPath).isFile()) throw new Error("not a file");
  } catch {
    failure(testCase.id, "CASE_PATH_OUTSIDE_CORPUS");
    continue;
  }
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  } catch (error) {
    failure(testCase.id, `MANIFEST_READ_FAILED:${error.name}`);
    continue;
  }
  const receipt = validateManifest(manifest);
  completed += 1;
  if (receipt.status !== testCase.expectedStatus) {
    failures.push({id: testCase.id, reason: `STATUS_MISMATCH:${testCase.expectedStatus}:${receipt.status}`});
  }
  if (JSON.stringify(receipt.reasonCodes) !== JSON.stringify(testCase.expectedReasonCodes)) {
    failures.push({id: testCase.id, reason: "REASON_CODES_MISMATCH"});
  }
}

const result = {
  implementation: "javascript-experimental",
  corpusVersion,
  status: failures.length === 0 ? "PASS" : "HOLD",
  declaredCases: cases.length,
  completedCases: completed,
  failures,
  executionAttempted: false,
  admissionAuthorized: false,
};
console.log(JSON.stringify(result, null, 2));
process.exitCode = failures.length === 0 ? 0 : 2;

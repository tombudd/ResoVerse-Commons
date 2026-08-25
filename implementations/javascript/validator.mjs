import { createHash } from "node:crypto";
import path from "node:path";

const ID = /^[a-z0-9]+(?:[._-][a-z0-9]+)*$/;
const SEMVER = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const TOP = new Set(["schemaVersion", "id", "version", "name", "description", "entrypoint", "provenance", "dependencies", "permissions", "limits", "learningUse"]);
const PROVENANCE = new Set(["sourceUrl", "license", "authors", "rightsToSubmit"]);
const PERMISSIONS = new Set(["network", "filesystemRead", "filesystemWrite", "environment", "subprocess"]);
const LIMITS = new Set(["wallTimeSeconds", "memoryMiB"]);
const LEARNING = new Set(["allowedInputs", "consent", "automaticPromotion"]);
const LEARNING_INPUTS = new Set(["source_code", "evaluations", "counterexamples"]);

function object(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (!object(value)) return value;
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]));
}

function jsonCompatible(value, seen = new Set()) {
  if (value === null || ["boolean", "string"].includes(typeof value)) return true;
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value !== "object" || seen.has(value)) return false;
  seen.add(value);
  const valid = Array.isArray(value)
    ? value.every((item) => jsonCompatible(item, seen))
    : Object.values(value).every((item) => jsonCompatible(item, seen));
  seen.delete(value);
  return valid;
}

function safeRelative(value) {
  return typeof value === "string"
    && value.trim() !== ""
    && !/[\\\x00-\x1f\x7f]/u.test(value)
    && value !== "."
    && !value.startsWith("./")
    && !value.endsWith("/")
    && !value.includes("//")
    && !path.posix.isAbsolute(value)
    && !/^[A-Za-z]:/u.test(value)
    && !value.split("/").includes("..")
    && path.posix.normalize(value) === value;
}

function validSourceUrl(value) {
  if (typeof value !== "string" || value === "" || [...value].some((character) => {
    const code = character.codePointAt(0);
    return code < 33 || code > 126;
  })) return false;
  try {
    const parsed = new URL(value);
    const hostname = parsed.hostname.replace(/^\[|\]$/gu, "");
    const validHost = hostname.includes(":") || (
      hostname.length <= 253
      && hostname.split(".").every((label) => /^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$/u.test(label))
    );
    return ["http:", "https:"].includes(parsed.protocol)
      && parsed.username === "" && parsed.password === "" && validHost;
  } catch {
    return false;
  }
}

function fields(value, expected, location, reasons) {
  if (!object(value)) return false;
  for (const key of [...expected].sort()) {
    if (!Object.hasOwn(value, key)) reasons.push(`MISSING_REQUIRED_FIELD:${location}${key}`);
  }
  for (const key of Object.keys(value).sort()) {
    if (!expected.has(key)) reasons.push(`UNKNOWN_FIELD:${location}${key}`);
  }
  return true;
}

export function validateManifest(candidate) {
  const reasons = [];
  let digest = null;
  let manifest = candidate;
  if (jsonCompatible(candidate)) {
    digest = createHash("sha256").update(JSON.stringify(canonical(candidate))).digest("hex");
  } else {
    reasons.push("INPUT_NOT_JSON_COMPATIBLE");
    manifest = {};
  }
  if (!object(manifest)) {
    manifest = {};
    reasons.push("MANIFEST_MUST_BE_OBJECT");
  }

  fields(manifest, TOP, "", reasons);
  if (manifest.schemaVersion !== "1.0") reasons.push("UNSUPPORTED_SCHEMA_VERSION");
  if (typeof manifest.id !== "string" || !ID.test(manifest.id)) reasons.push("INVALID_CAPABILITY_ID");
  if (typeof manifest.version !== "string" || !SEMVER.test(manifest.version)) reasons.push("INVALID_SEMANTIC_VERSION");
  if (typeof manifest.name !== "string" || manifest.name.trim() === "") reasons.push("INVALID_NAME");
  if (typeof manifest.description !== "string" || manifest.description.trim().length < 20) reasons.push("INVALID_DESCRIPTION");
  if (!safeRelative(manifest.entrypoint)) reasons.push("UNSAFE_ENTRYPOINT_PATH");
  if (!Array.isArray(manifest.dependencies) || manifest.dependencies.length !== 0) reasons.push("V1_DEPENDENCIES_PROHIBITED");

  if (!fields(manifest.provenance, PROVENANCE, "provenance.", reasons)) {
    reasons.push("INVALID_PROVENANCE");
  } else {
    if (!validSourceUrl(manifest.provenance.sourceUrl)) reasons.push("INVALID_SOURCE_URL");
    if (typeof manifest.provenance.license !== "string" || manifest.provenance.license.trim() === "") reasons.push("INVALID_LICENSE");
    if (!Array.isArray(manifest.provenance.authors) || manifest.provenance.authors.length === 0 || !manifest.provenance.authors.every((author) => typeof author === "string" && author.trim() !== "")) reasons.push("MISSING_AUTHORS");
    if (manifest.provenance.rightsToSubmit !== true) reasons.push("RIGHTS_TO_SUBMIT_NOT_CERTIFIED");
  }

  if (!fields(manifest.permissions, PERMISSIONS, "permissions.", reasons)) {
    reasons.push("INVALID_PERMISSIONS");
  } else {
    const permission = manifest.permissions;
    if (!Array.isArray(permission.network) || permission.network.length !== 0) reasons.push("V1_NETWORK_PERMISSION_DENIED");
    if (!Array.isArray(permission.filesystemRead) || !permission.filesystemRead.every(safeRelative)) reasons.push("INVALID_FILESYSTEM_READ_SCOPE");
    if (!Array.isArray(permission.filesystemWrite) || permission.filesystemWrite.length !== 0) reasons.push("V1_FILESYSTEM_WRITE_PERMISSION_DENIED");
    if (!Array.isArray(permission.environment) || permission.environment.length !== 0) reasons.push("V1_ENVIRONMENT_ACCESS_DENIED");
    if (permission.subprocess !== false) reasons.push("V1_SUBPROCESS_PERMISSION_DENIED");
  }

  if (!fields(manifest.limits, LIMITS, "limits.", reasons)) {
    reasons.push("INVALID_LIMITS");
  } else {
    if (!Number.isInteger(manifest.limits.wallTimeSeconds) || manifest.limits.wallTimeSeconds < 1 || manifest.limits.wallTimeSeconds > 30) reasons.push("INVALID_WALL_TIME_LIMIT");
    if (!Number.isInteger(manifest.limits.memoryMiB) || manifest.limits.memoryMiB < 16 || manifest.limits.memoryMiB > 512) reasons.push("INVALID_MEMORY_LIMIT");
  }

  if (!fields(manifest.learningUse, LEARNING, "learningUse.", reasons)) {
    reasons.push("INVALID_LEARNING_USE");
  } else {
    const allowed = manifest.learningUse.allowedInputs;
    if (!Array.isArray(allowed) || !allowed.every((item) => typeof item === "string" && LEARNING_INPUTS.has(item)) || new Set(allowed).size !== allowed.length) reasons.push("INVALID_LEARNING_INPUTS");
    if (manifest.learningUse.automaticPromotion !== false) reasons.push("AUTOMATIC_PROMOTION_PROHIBITED");
    if (manifest.learningUse.consent !== "explicit_contribution") reasons.push("EXPLICIT_CONTRIBUTION_CONSENT_REQUIRED");
  }

  const reasonCodes = [...new Set(reasons)].sort();
  return {
    receiptVersion: "1.0",
    status: reasonCodes.length === 0 ? "PASS" : "HOLD",
    canonicalManifestSha256: digest,
    submittedBytesSha256: null,
    reasonCodes,
    executionAttempted: false,
    memoryPromotionAuthorized: false,
    productionActivationAuthorized: false,
  };
}

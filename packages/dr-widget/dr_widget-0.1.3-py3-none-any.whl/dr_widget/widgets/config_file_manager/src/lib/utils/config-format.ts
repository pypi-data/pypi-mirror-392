export type NormalizedConfigPayload = {
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
  version?: string;
  savedAt?: string;
};

export function normalizeConfigPayload(
  payload: unknown,
): NormalizedConfigPayload {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return { data: {}, metadata: {} };
  }

  const record = payload as Record<string, unknown>;
  const dataCandidate = record["data"];
  let data: Record<string, unknown>;
  const metadataCandidate = record["metadata"];
  const metadata: Record<string, unknown> =
    metadataCandidate &&
    typeof metadataCandidate === "object" &&
    !Array.isArray(metadataCandidate)
      ? { ...(metadataCandidate as Record<string, unknown>) }
      : {};

  if (
    dataCandidate &&
    typeof dataCandidate === "object" &&
    !Array.isArray(dataCandidate)
  ) {
    data = dataCandidate as Record<string, unknown>;
  } else if (
    record["selections"] &&
    typeof record["selections"] === "object" &&
    !Array.isArray(record["selections"])
  ) {
    data = { selections: record["selections"] as Record<string, unknown> };
  } else {
    data = Object.fromEntries(
      Object.entries(record).filter(
        ([key]) =>
          key !== "version" && key !== "saved_at" && key !== "metadata",
      ),
    );
  }

  const versionValue = metadata["version"] ?? record["version"];
  const savedAtValue = metadata["saved_at"] ?? record["saved_at"];
  const version =
    typeof versionValue === "string"
      ? versionValue
      : typeof versionValue === "number"
        ? String(versionValue)
        : undefined;
  const savedAt = typeof savedAtValue === "string" ? savedAtValue : undefined;

  return {
    data,
    metadata,
    version,
    savedAt,
  };
}

export function buildWrappedPayload({
  data,
  version,
  savedAt,
  metadata,
}: {
  data: Record<string, unknown>;
  version?: string | null;
  savedAt?: string | null;
  metadata?: Record<string, unknown> | null;
}): Record<string, unknown> {
  const payloadMetadata: Record<string, unknown> = metadata
    ? { ...metadata }
    : {};

  if (version && version.trim().length > 0) {
    payloadMetadata.version = version;
  }

  if (savedAt && savedAt.trim().length > 0) {
    payloadMetadata.saved_at = savedAt;
  }

  const payload: Record<string, unknown> = {
    metadata: payloadMetadata,
    data,
  };

  return payload;
}

export function formatSavedAt(value: unknown): string | undefined {
  if (typeof value !== "string" || value.trim().length === 0) {
    return undefined;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsed);
}

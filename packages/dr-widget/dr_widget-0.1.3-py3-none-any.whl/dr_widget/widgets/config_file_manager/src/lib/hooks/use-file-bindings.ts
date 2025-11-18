import type { FileDropZoneProps } from "$lib/components/ui/file-drop-zone";

export type BoundFile = {
  name: string;
  size: number;
  type: string;
};

export type FileBinding = {
  file_count: number;
  files: string;
  error: string;
  current_state?: string | null;
  baseline_state?: string | null;
  config_file?: string | null;
  config_file_display?: string | null;
  version?: string | null;
  saved_at?: string | null;
};

const coerceString = (value?: string | null) =>
  typeof value === "string" ? value : (value ?? "");

export const normalizeBoundFiles = (
  files: unknown,
  limit?: number,
): BoundFile[] => {
  if (!Array.isArray(files)) return [];

  const validItems = files
    .filter(
      (item) =>
        item &&
        typeof item.name === "string" &&
        typeof item.size === "number" &&
        typeof item.type === "string",
    )
    .map((item) => ({
      name: item.name,
      size: item.size,
      type: item.type,
    }));

  const limitSize = typeof limit === "number" ? limit : validItems.length;
  return validItems.slice(0, limitSize);
};

export const readBindingFiles = (bindings: FileBinding): BoundFile[] => {
  if (!bindings?.files) return [];
  try {
    const parsed = JSON.parse(bindings.files) as unknown;
    return normalizeBoundFiles(parsed);
  } catch {
    return [];
  }
};

export const writeBindingFiles = (
  bindings: FileBinding,
  files: BoundFile[],
): void => {
  const normalized = normalizeBoundFiles(files);
  bindings.files = JSON.stringify(normalized);
  bindings.file_count = normalized.length;
};

export const writeBindingCurrentState = (
  bindings: FileBinding,
  contents?: string | null,
): void => {
  bindings.current_state = coerceString(contents);
};

export const writeBindingBaselineState = (
  bindings: FileBinding,
  contents?: string | null,
): void => {
  bindings.baseline_state = coerceString(contents);
};

export const writeBindingVersion = (
  bindings: FileBinding,
  version?: string | null,
): void => {
  bindings.version = coerceString(version);
};

export const writeBindingConfigFile = (
  bindings: FileBinding,
  path?: string | null,
): void => {
  bindings.config_file = coerceString(path);
};

export const writeBindingConfigFileDisplay = (
  bindings: FileBinding,
  path?: string | null,
): void => {
  bindings.config_file_display = coerceString(path);
};

export const writeBindingSavedAt = (
  bindings: FileBinding,
  timestamp?: string | null,
): void => {
  bindings.saved_at = coerceString(timestamp);
};

export const writeBindingError = (
  bindings: FileBinding,
  error?: string | null,
): void => {
  bindings.error = coerceString(error);
};

type UploadHandler = FileDropZoneProps["onUpload"];
type RejectHandler = NonNullable<FileDropZoneProps["onFileRejected"]>;

export function createFileBindingHandlers({
  bindings,
  maxFiles,
}: {
  bindings: FileBinding;
  maxFiles?: number;
}) {
  const maxFileCount = Number.isFinite(maxFiles) ? maxFiles : undefined;

  const enforceLimit = (files: BoundFile[]): BoundFile[] => {
    if (!maxFileCount) return files;
    return files.slice(0, maxFileCount);
  };

  const readBoundFiles = (): BoundFile[] => readBindingFiles(bindings);

  const writeBoundFiles = (files: BoundFile[]): void => {
    writeBindingFiles(bindings, enforceLimit(files));
  };

  const handleUpload: UploadHandler = async (files) => {
    const nextFiles = files
      .slice(0, maxFileCount ?? files.length)
      .map((file) => ({
        name: file.name,
        size: file.size,
        type: file.type,
      }));

    if (nextFiles.length === 0) return;

    writeBoundFiles(nextFiles);
    writeBindingError(bindings, "");
  };

  const handleFileRejected: RejectHandler = ({ reason, file }) => {
    writeBindingError(bindings, `${file.name}: ${reason}`);
  };

  const removeFile = (index: number): void => {
    const current = readBoundFiles();
    current.splice(index, 1);
    writeBoundFiles(current);

    if (current.length === 0) {
      writeBindingError(bindings, "");
    }
  };

  return {
    bindings,
    readBoundFiles,
    writeBoundFiles,
    handleUpload,
    handleFileRejected,
    removeFile,
    writeCurrentState: (contents?: string | null) =>
      writeBindingCurrentState(bindings, contents),
    writeBaselineState: (contents?: string | null) =>
      writeBindingBaselineState(bindings, contents),
    writeVersion: (version?: string | null) =>
      writeBindingVersion(bindings, version),
    writeConfigFile: (path?: string | null) =>
      writeBindingConfigFile(bindings, path),
    writeConfigFileDisplay: (path?: string | null) =>
      writeBindingConfigFileDisplay(bindings, path),
    writeSavedAt: (timestamp?: string | null) =>
      writeBindingSavedAt(bindings, timestamp),
    writeError: (error?: string | null) => writeBindingError(bindings, error),
  };
}

<script lang="ts">
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Badge } from "$lib/components/ui/badge/index.js";
  import ConfigViewerPanel from "$lib/components/file-drop/ConfigViewerPanel.svelte";
  import { buildWrappedPayload } from "$lib/utils/config-format";
  import {
    writeBindingBaselineState,
    writeBindingConfigFile,
    writeBindingConfigFileDisplay,
    writeBindingError,
    writeBindingSavedAt,
    writeBindingVersion,
    type FileBinding,
  } from "$lib/hooks/use-file-bindings";

  type SaveFilePickerOptions = {
    suggestedName?: string;
    startIn?: BrowserFileHandle;
    types?: Array<{ description?: string; accept: Record<string, string[]> }>;
  };

  type BrowserFileHandle = {
    readonly kind?: "file" | "directory";
    name: string;
    createWritable: () => Promise<{
      write: (data: Blob | BufferSource | string) => Promise<void>;
      close: () => Promise<void>;
      abort?: () => Promise<void>;
    }>;
    getFile?: () => Promise<File>;
    requestPermission?: (options?: { mode?: "read" | "readwrite" }) => Promise<PermissionState>;
  };

  type FileSystemAccessWindow = Window &
    typeof globalThis & {
      showSaveFilePicker?: (options?: SaveFilePickerOptions) => Promise<BrowserFileHandle>;
    };

  const {
    bindings,
    rawConfig,
    baselineConfig,
    defaultFileName = "config.json",
    saveTargetLabel,
    dirty = false,
    currentVersion = "",
    canEditVersion = false,
  } = $props<{
    bindings: FileBinding;
    rawConfig?: string;
    baselineConfig?: unknown;
    defaultFileName?: string;
    saveTargetLabel?: string;
    dirty?: boolean;
    currentVersion?: string;
    canEditVersion?: boolean;
  }>();

  const isAbsolutePath = (value?: string): boolean => {
    if (!value) return false;
    const trimmed = value.trim();
    if (!trimmed) return false;
    return trimmed.startsWith("/") || trimmed.startsWith("\\") || /^[A-Za-z]:[\\/]/.test(trimmed);
  };

  const extractFileName = (value?: string): string | undefined => {
    if (!value) return undefined;
    const trimmed = value.trim();
    if (!trimmed) return undefined;
    const parts = trimmed.split(/[\\/]+/).filter(Boolean);
    return parts.length > 0 ? parts[parts.length - 1] : trimmed;
  };

  const dirname = (value?: string): string => {
    if (!value) return "";
    const trimmed = value.trim();
    if (!trimmed) return "";
    const windowsDrive = trimmed.match(/^[A-Za-z]:[\\/]/)?.[0];
    const sep = trimmed.includes("\\") && !trimmed.includes("/") ? "\\" : "/";
    const normalized = trimmed.replace(/[\\/]+/g, sep);
    const parts = normalized.split(sep);
    if (parts.length <= 1) {
      return windowsDrive ?? (normalized.startsWith(sep) ? sep : "");
    }
    parts.pop();
    let dir = parts.join(sep);
    if (windowsDrive && !dir.startsWith(windowsDrive)) {
      dir = `${windowsDrive}${dir}`;
    } else if (normalized.startsWith(sep) && !dir.startsWith(sep)) {
      dir = `${sep}${dir}`;
    }
    return dir;
  };

  const joinPath = (dir: string, leaf: string): string => {
    if (!dir) return leaf;
    const sep = dir.includes("\\") && !dir.includes("/") ? "\\" : "/";
    const normalizedDir = dir === sep || dir.endsWith(sep) ? dir : `${dir}${sep}`;
    return `${normalizedDir}${leaf}`;
  };

  const resolveAbsoluteTarget = (candidate?: string, fallback?: string | null): string => {
    const trimmedCandidate = candidate?.trim();
    if (!trimmedCandidate) {
      return fallback?.trim() ?? "";
    }
    if (isAbsolutePath(trimmedCandidate)) {
      return trimmedCandidate;
    }
    const fallbackValue = fallback?.trim() ?? "";
    if (fallbackValue && isAbsolutePath(fallbackValue)) {
      const parent = dirname(fallbackValue);
      if (parent) {
        return joinPath(parent, trimmedCandidate);
      }
    }
    return trimmedCandidate;
  };

  let chosenFileName = $state(defaultFileName);
  let lastSavedMessage = $state("");
  let saveError = $state("");
  let saving = $state(false);
  let versionInput = $state(currentVersion);
  const parsedConfig = $derived.by(() => {
    if (!rawConfig) return undefined;

    try {
      return JSON.parse(rawConfig);
    } catch {
      return undefined;
    }
  });

  const derivedSavePath = (candidate?: string | null) => {
    const value = candidate?.trim();
    if (value && isAbsolutePath(value)) {
      return value;
    }
    return undefined;
  };

  const buildSaveMetadataEntry = (absolutePath?: string | null, label?: string | null) => {
    const resolvedPath = derivedSavePath(absolutePath);
    if (resolvedPath) {
      return { save_path: resolvedPath };
    }
    const trimmedLabel = label?.trim();
    if (trimmedLabel) {
      return { save_path: trimmedLabel };
    }
    return undefined;
  };

  const wrappedPreview = $derived.by(() => {
    if (!parsedConfig || typeof parsedConfig !== "object" || Array.isArray(parsedConfig)) {
      return undefined;
    }

    const versionCandidate = versionInput?.trim() || currentVersion?.trim() || undefined;
    const metadataPreviewLabel =
      bindings.config_file_display || bindings.config_file || defaultFileName || chosenFileName;
    const metadataEntry = buildSaveMetadataEntry(bindings.config_file, metadataPreviewLabel);
    const payload = buildWrappedPayload({
      data: parsedConfig as Record<string, unknown>,
      version: versionCandidate,
      savedAt: undefined,
      metadata: metadataEntry,
    });

    return {
      json: JSON.stringify(payload, null, 2),
      data: payload,
    };
  });

  const fsWindow: FileSystemAccessWindow | undefined =
    typeof window !== "undefined"
      ? (window as FileSystemAccessWindow)
      : undefined;

  const supportsFileSystemAccess = Boolean(fsWindow?.showSaveFilePicker);
  const versionInputId = `config-version-${Math.random().toString(36).slice(2)}`;
  const defaultSaveLabel = $derived.by(() => {
    const explicitLabel = saveTargetLabel?.trim();
    if (explicitLabel) return explicitLabel;
    const fileName = defaultFileName?.trim();
    if (fileName) return fileName;
    return "config.json";
  });

  $effect(() => {
    if (defaultFileName && !chosenFileName) {
      chosenFileName = defaultFileName;
    }
  });

  let lastDefaultFileName = $state(defaultFileName);
  $effect(() => {
    if (defaultFileName !== lastDefaultFileName) {
      chosenFileName = defaultFileName;
      lastDefaultFileName = defaultFileName;
    }
  });

  $effect(() => {
    versionInput = currentVersion ?? "";
  });

  const buildPickerOptions = (): SaveFilePickerOptions => {
    const options: SaveFilePickerOptions = {
      suggestedName: chosenFileName || defaultFileName,
    };

    return options;
  };

  const pickHandle = async () => {
    if (!supportsFileSystemAccess || !fsWindow?.showSaveFilePicker) return null;
    try {
      const handle = await fsWindow.showSaveFilePicker(buildPickerOptions());
      if (handle.name) {
        chosenFileName = handle.name;
      }
      saveError = "";
      return handle;
    } catch (error) {
      if ((error as DOMException).name === "AbortError") {
        return null;
      }
      const message = (error as Error)?.message ?? "Unable to choose file location.";
      saveError = message;
      writeBindingError(bindings, message);
      return null;
    }
  };

  const downloadFallback = (contents: string, fileName: string) => {
    const blob = new Blob([contents], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const handleSave = async () => {
    const latestRawConfig = bindings.current_state ?? rawConfig;
    if (!latestRawConfig) {
      saveError = "No config data available to save.";
      writeBindingError(bindings, saveError);
      return;
    }

    const dataObject =
      parsedConfig && typeof parsedConfig === "object" && !Array.isArray(parsedConfig)
        ? (parsedConfig as Record<string, unknown>)
        : undefined;

    if (!dataObject) {
      saveError = "Config JSON must be an object.";
      writeBindingError(bindings, saveError);
      return;
    }

    saveError = "";
    lastSavedMessage = "";

    const timestamp = new Date().toISOString();
    const trimmedInput = versionInput?.trim();
    const fallbackVersion = currentVersion?.trim();
    const normalizedVersion = trimmedInput || fallbackVersion || "default_v0";
    if ((bindings.version ?? "") !== normalizedVersion) {
      writeBindingVersion(bindings, normalizedVersion);
      versionInput = normalizedVersion;
    }
    const targetFileName = chosenFileName || defaultFileName;
    const absoluteTargetPath = resolveAbsoluteTarget(targetFileName, bindings.config_file ?? undefined);
    const fallbackName = absoluteTargetPath || "config.json";
    const preferredLabel = extractFileName(absoluteTargetPath) ?? targetFileName ?? fallbackName;

    const buildSerializedConfig = (labelChoice?: string | null) => {
      const metadataEntry = buildSaveMetadataEntry(absoluteTargetPath, labelChoice ?? preferredLabel);
      const payload = buildWrappedPayload({
        data: dataObject,
        version: normalizedVersion,
        savedAt: timestamp,
        metadata: metadataEntry,
      });
      return {
        metadataEntry,
        label: labelChoice ?? preferredLabel,
        serialized: `${JSON.stringify(payload, null, 2)}\n`,
      };
    };

    let { serialized: serializedConfig, label: currentLabel } = buildSerializedConfig(preferredLabel);
    const downloadName = currentLabel || fallbackName;

    const persistSuccessMetadata = (options?: { absolutePath?: string; label?: string }) => {
      const baselineSource = bindings.current_state ?? latestRawConfig ?? "";
      writeBindingBaselineState(bindings, baselineSource);
      const nextAbsolutePath = options?.absolutePath ?? absoluteTargetPath;
      const savedLabel =
        options?.label ?? (nextAbsolutePath ? extractFileName(nextAbsolutePath) : undefined) ?? downloadName;
      if (nextAbsolutePath && isAbsolutePath(nextAbsolutePath)) {
        writeBindingConfigFile(bindings, nextAbsolutePath);
        writeBindingConfigFileDisplay(bindings, savedLabel);
      } else if (savedLabel) {
        writeBindingConfigFileDisplay(bindings, savedLabel);
      }
      writeBindingSavedAt(bindings, timestamp);
      writeBindingError(bindings, "");
      return savedLabel;
    };

    if (!supportsFileSystemAccess) {
      downloadFallback(serializedConfig, downloadName);
      const persistedLabel = persistSuccessMetadata({ label: currentLabel });
      lastSavedMessage = `Downloaded ${persistedLabel}`;
      return;
    }

    try {
      saving = true;
      const handle = await pickHandle();
      if (!handle) {
        saving = false;
        return;
      }

      await handle.requestPermission?.({ mode: "readwrite" });

      currentLabel = handle.name ?? currentLabel;
      ({ serialized: serializedConfig } = buildSerializedConfig(currentLabel));

      const writable = await handle.createWritable();
      try {
        const fileBlob = new Blob([serializedConfig], { type: "application/json" });
        await writable.write(fileBlob);
        await writable.close();
      } catch (writeError) {
        if (typeof writable.abort === "function") {
          await writable.abort();
        }
        throw writeError;
      }

      const persistedLabel = persistSuccessMetadata({ label: currentLabel });
      const savedLabel = persistedLabel ?? currentLabel ?? downloadName;
      lastSavedMessage = `Saved ${savedLabel} at ${new Date(timestamp).toLocaleString()}`;
      if (handle.name) {
        chosenFileName = handle.name;
      }
      saveError = "";
    } catch (error) {
      const message = (error as Error)?.message ?? "Failed to save config.";
      saveError = message;
      writeBindingError(bindings, message);
    } finally {
      saving = false;
    }
  };
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Save Config</Card.Title>
    <Card.Description>
      {#if dirty}
        Choose where to write the modified configuration.
      {:else}
        Config matches the last saved version.
      {/if}
    </Card.Description>
  </Card.Header>
  <Card.Content class="space-y-4">
    <div class="space-y-2">
      <label class="text-sm font-medium text-zinc-600 dark:text-zinc-300" for={versionInputId}>
        Version
      </label>
      <input
        class="w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-70 dark:border-zinc-700 dark:bg-zinc-900"
        id={versionInputId}
        value={versionInput}
        placeholder="e.g. 1.0.0"
        disabled={!canEditVersion || !rawConfig}
        oninput={(event) => {
          const nextValue = (event.target as HTMLInputElement).value;
          versionInput = nextValue;
          const trimmed = nextValue.trim();
          writeBindingVersion(bindings, trimmed || "");
        }}
      />
    </div>

    <div class="rounded-md border border-zinc-100 bg-zinc-50 px-3 py-2 text-xs text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900/60 dark:text-zinc-300">
      {#if supportsFileSystemAccess}
        <p>
          Default file name:
          <span class="font-medium text-zinc-900 dark:text-zinc-100">{defaultSaveLabel}</span>. You'll choose the folder after clicking
          <span class="font-medium">Save</span>.
        </p>
      {:else}
        <p>
          Download name:
          <span class="font-medium text-zinc-900 dark:text-zinc-100">{defaultSaveLabel}</span>. Your browser will download the file directly.
        </p>
      {/if}
    </div>

    <div class="flex flex-wrap items-center gap-3">
      {#if dirty}
        <Badge variant="secondary" class="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-200">
          Unsaved changes
        </Badge>
      {:else}
        <Badge variant="secondary">Up to date</Badge>
      {/if}
    </div>

    <div class="flex flex-wrap gap-2">
      <Button onclick={handleSave} disabled={!rawConfig || saving}>
        {saving ? "Saving…" : supportsFileSystemAccess ? "Save" : "Download"}
      </Button>
    </div>

    {#if lastSavedMessage}
      <p class="text-sm text-emerald-600 dark:text-emerald-400">{lastSavedMessage}</p>
    {/if}

    {#if saveError}
      <p class="text-sm text-red-500 dark:text-red-400">{saveError}</p>
    {/if}

    <ConfigViewerPanel
      data={parsedConfig}
      rawJson={rawConfig}
      baselineData={baselineConfig}
      {dirty}
      wrappedJson={wrappedPreview?.json}
      wrappedData={wrappedPreview?.data}
    />
  </Card.Content>
</Card.Root>

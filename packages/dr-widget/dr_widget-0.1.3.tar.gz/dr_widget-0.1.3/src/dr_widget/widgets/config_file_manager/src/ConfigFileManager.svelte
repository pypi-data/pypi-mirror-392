<script lang="ts">
  import * as Tabs from "$lib/components/ui/tabs/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Badge } from "$lib/components/ui/badge/index.js";

  import BrowseConfigsPanel from "$lib/components/file-drop/BrowseConfigsPanel.svelte";
  import LoadedConfigPreview from "$lib/components/file-drop/LoadedConfigPreview.svelte";
  import SaveConfigPanel from "$lib/components/file-drop/SaveConfigPanel.svelte";
  import {
    createFileBindingHandlers,
    type BoundFile,
    type FileBinding,
  } from "$lib/hooks/use-file-bindings";
  import {
    buildWrappedPayload,
    formatSavedAt,
    normalizeConfigPayload,
  } from "$lib/utils/config-format";

const { bindings } = $props<{
  bindings: FileBinding;
}>();

const maxFiles = 1;
const bindingHandlers = createFileBindingHandlers({
  bindings,
  maxFiles,
});

const parseJsonObject = (value?: string | null) => {
  if (!value) return undefined;
  try {
    const parsed = JSON.parse(value);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    return undefined;
  }
  return undefined;
};

const canonicalizeState = (value?: string | null) => {
  const parsed = parseJsonObject(value);
  if (parsed) {
    try {
      return JSON.stringify(parsed);
    } catch {
      return (value ?? "").trim();
    }
  }
  return (value ?? "").trim();
};

const buildMetadataSnapshot = () => {
  const snapshot: Record<string, string> = {};
  const trimmedVersion = bindings.version?.trim();
  if (trimmedVersion) {
    snapshot.version = trimmedVersion;
  }
  return snapshot;
};

const canonicalizeMetadata = (metadata?: Record<string, string>) => {
  if (!metadata) return "";
  const entries = Object.entries(metadata)
    .map(([key, value]) => [key, typeof value === "string" ? value.trim() : value])
    .filter((entry): entry is [string, string] => Boolean(entry[1] && entry[1].length > 0));
  if (entries.length === 0) {
    return "";
  }
  entries.sort(([a], [b]) => a.localeCompare(b));
  return JSON.stringify(Object.fromEntries(entries));
};

const extractFileName = (value?: string | null) => {
  if (!value) return undefined;
  const parts = value.split(/[\\/]+/).filter(Boolean);
  if (parts.length === 0) return value;
  return parts[parts.length - 1];
};

const hasMetadataEntries = (metadata?: Record<string, unknown>) =>
  Boolean(metadata && Object.keys(metadata).length > 0);

const parsedFiles = $derived(bindingHandlers.readBoundFiles());
const baselineParsed = $derived.by(() => parseJsonObject(bindings.baseline_state));
const metadataSnapshot = $derived.by(() => buildMetadataSnapshot());
let lastSavedMetadata = $state<Record<string, string>>(buildMetadataSnapshot());
let lastBaselineSignature = $state(bindings.baseline_state ?? "");
const metadataDirty = $derived.by(
  () => canonicalizeMetadata(metadataSnapshot) !== canonicalizeMetadata(lastSavedMetadata),
);
const isDirty = $derived.by(
  () =>
    canonicalizeState(bindings.current_state) !== canonicalizeState(bindings.baseline_state) || metadataDirty,
);
const selectedConfigVersion = $derived.by(() => bindings.version ?? "");
const canEditSelectedConfigVersion = $derived.by(() => Boolean(bindings.current_state && bindings.current_state.trim().length > 0));
const configFileDisplayName = $derived.by(
  () => bindings.config_file_display || extractFileName(bindings.config_file) || undefined,
);

let previewFile = $state<BoundFile | undefined>(undefined);
let previewText = $state<string | undefined>(bindings.current_state ?? undefined);
let previewJson = $state<unknown | undefined>(() => {
  if (!bindings.current_state) return undefined;
  try {
    return JSON.parse(bindings.current_state);
  } catch {
    return undefined;
  }
});
let loadedMetadataExtras = $state<Record<string, unknown>>({});
const normalizedPreview = $derived.by(() => {
  if (!previewJson || typeof previewJson !== "object") return undefined;
  return normalizeConfigPayload(previewJson);
});
const normalizedPreviewData = $derived.by(() => {
  if (!normalizedPreview) return undefined;
  return JSON.stringify(normalizedPreview.data, null, 2);
});
const normalizedPreviewParsed = $derived.by(() => normalizedPreview?.data);
  let managerOpen = $state(false);
  let activeTab = $state("find");
  let lastLoadedFileName = $state<string | undefined>(undefined);
  let loadedConfigSummary = $state<
    | {
        name?: string;
        savedAt?: string;
        version?: string;
        rawText?: string;
        parsed?: unknown;
        wrappedRawText?: string;
        wrappedParsed?: unknown;
      }
    | undefined
  >(undefined);
  let showLoadedPreview = $state(false);
  let previewFromLoaded = $state(false);
  let loadedConfigPath = $state<string | undefined>(undefined);
  let lastObservedSavedAt = $state<string | undefined>(bindings.saved_at ?? undefined);
  const defaultSaveTarget = $derived.by(
    () =>
      bindings.config_file_display ||
      bindings.config_file ||
      loadedConfigPath ||
      lastLoadedFileName ||
      "config.json",
  );
  const defaultSaveLabel = $derived.by(
    () =>
      bindings.config_file ||
      loadedConfigPath ||
      defaultSaveTarget,
  );

const computeBindingMetadataFallback = () => {
  const displayLabel = bindings.config_file_display?.trim();
  if (displayLabel) {
    return { save_path: displayLabel };
  }
  const resolvedPath = bindings.config_file?.trim();
  if (resolvedPath) {
    return { save_path: resolvedPath };
  }
  const fallbackLabel = loadedConfigPath || lastLoadedFileName;
  if (fallbackLabel) {
    return { save_path: fallbackLabel };
  }
  return undefined;
};

const bindingSaveMetadata = $derived.by(() => {
  if (hasMetadataEntries(loadedMetadataExtras)) {
    return loadedMetadataExtras;
  }
  return computeBindingMetadataFallback();
});

const previewWrappedPayload = $derived.by(() => {
  if (!normalizedPreview) return undefined;
  const previewMetadata = hasMetadataEntries(normalizedPreview.metadata)
    ? normalizedPreview.metadata
    : bindingSaveMetadata;
  return buildWrappedPayload({
    data: normalizedPreview.data,
    version: normalizedPreview.version ?? bindings.version ?? undefined,
    savedAt: normalizedPreview.savedAt ?? bindings.saved_at ?? undefined,
    metadata: previewMetadata,
  });
});
const previewWrappedJson = $derived.by(() =>
  previewWrappedPayload ? JSON.stringify(previewWrappedPayload, null, 2) : undefined,
);

  $effect(() => {
    const latestPath = bindings.config_file?.trim();
    if (latestPath && latestPath !== loadedConfigPath) {
      loadedConfigPath = latestPath;
    }
  });

  $effect(() => {
    const latestDisplay = bindings.config_file_display?.trim();
    if (latestDisplay && latestDisplay !== lastLoadedFileName) {
      lastLoadedFileName = latestDisplay;
    }
  });

  $effect(() => {
    const savedAt = bindings.saved_at?.trim() ?? "";
    if (savedAt && savedAt !== lastObservedSavedAt) {
      previewFromLoaded = false;
      showLoadedPreview = false;
      bindingHandlers.writeError("");
      lastObservedSavedAt = savedAt;
      lastSavedMetadata = buildMetadataSnapshot();
      const latestMetadata = computeBindingMetadataFallback();
      loadedMetadataExtras = latestMetadata ?? {};
      const fallbackPath = bindings.config_file?.trim() || bindings.config_file_display?.trim();
      if (fallbackPath) {
        loadedConfigPath = fallbackPath;
      }
    } else if (!savedAt && lastObservedSavedAt) {
      lastObservedSavedAt = undefined;
      lastSavedMetadata = buildMetadataSnapshot();
      loadedMetadataExtras = {};
    }
  });

  $effect(() => {
    const baselineSignature = bindings.baseline_state ?? "";
    if (baselineSignature !== lastBaselineSignature) {
      lastBaselineSignature = baselineSignature;
      lastSavedMetadata = buildMetadataSnapshot();
    }
  });

  const computeByteSize = (input: string): number => {
    if (typeof TextEncoder !== "undefined") {
      return new TextEncoder().encode(input).byteLength;
    }
    return input.length;
  };

  const resetPreviewState = () => {
    previewFile = undefined;
    previewText = undefined;
    previewJson = undefined;
  };

  // previewText
  $effect(() => {
    if (!previewText) {
      previewJson = undefined;
      return;
    }

    try {
      previewJson = JSON.parse(previewText);
    } catch {
      previewJson = undefined;
    }
  });

  // parsedFiles, previewFile, previewFromLoaded
  $effect(() => {
    if (parsedFiles.length === 0 && previewFile && !previewFromLoaded) {
      resetPreviewState();
    }
  });

const previewSavedAt = $derived.by(() => formatSavedAt(normalizedPreview?.savedAt ?? bindings.saved_at));

const previewVersion = $derived.by(() => normalizedPreview?.version);

  // managerOpen, isDirty
  $effect(() => {
    if (!managerOpen) return;
    activeTab = isDirty ? "save" : "find";
  });

  // current_state and metadata summary
  $effect(() => {
    const raw = bindings.current_state;
    if (!raw || raw.trim().length === 0) {
      loadedConfigSummary = undefined;
      loadedMetadataExtras = {};
      previewFromLoaded = false;
      showLoadedPreview = false;
      lastLoadedFileName = undefined;
      loadedConfigPath = undefined;
      if (!managerOpen) {
        resetPreviewState();
      }
      return;
    }

    const parsed = parseJsonObject(raw) ?? {};
    const savedAtValue = (() => {
      const value = bindings.saved_at?.trim();
      return value ? value : undefined;
    })();
    const metadataExtras = bindingSaveMetadata;
    const wrappedPayload = buildWrappedPayload({
      data: parsed,
      version: bindings.version ?? undefined,
      savedAt: savedAtValue,
      metadata: metadataExtras,
    });
    const wrappedJson = JSON.stringify(wrappedPayload, null, 2);

    const savedAtLabel = savedAtValue ? formatSavedAt(savedAtValue) : undefined;

    loadedConfigSummary = {
      name: configFileDisplayName || lastLoadedFileName || loadedConfigSummary?.name || "Config loaded",
      savedAt: savedAtLabel,
      version: bindings.version ?? undefined,
      rawText: raw,
      parsed,
      wrappedRawText: wrappedJson,
      wrappedParsed: wrappedPayload,
    };

    if (!previewFromLoaded && !managerOpen) {
      previewText = raw;
      previewJson = parsed;
    }
  });

  const handleUpload = async (files: File[]) => {
    const [file] = files;
    if (!file) return;

    const fileText = await file.text();

    await bindingHandlers.handleUpload([file]);

    previewFile = {
      name: file.name,
      size: file.size,
      type: file.type,
    };
    previewText = fileText;
    bindingHandlers.writeError("");
    previewFromLoaded = false;
    loadedMetadataExtras = {};
  };

  const handleRemove = () => {
    if (previewFromLoaded) {
      bindingHandlers.writeCurrentState("");
      bindingHandlers.writeBaselineState("");
      bindingHandlers.writeVersion("");
      bindingHandlers.writeConfigFile("");
      bindingHandlers.writeConfigFileDisplay("");
      bindingHandlers.writeSavedAt("");
      loadedConfigSummary = undefined;
      previewFromLoaded = false;
      showLoadedPreview = false;
      lastLoadedFileName = undefined;
      loadedConfigPath = undefined;
      loadedMetadataExtras = {};
      bindingHandlers.writeError("");
      resetPreviewState();
      return;
    }

    if (parsedFiles.length > 0) {
      bindingHandlers.removeFile(0);
    }
    bindingHandlers.writeError("");
    resetPreviewState();
    loadedConfigPath = undefined;
    bindingHandlers.writeConfigFileDisplay("");
    bindingHandlers.writeSavedAt("");
    loadedMetadataExtras = {};
  };

  const handleLoadConfig = () => {
    if (!previewText) {
      bindingHandlers.writeError("Unable to load config: missing file contents.");
      return;
    }

    lastLoadedFileName = previewFile?.name ?? lastLoadedFileName;
    const summaryName = lastLoadedFileName ?? previewFile?.name ?? "Config loaded";

    let parsedFile: unknown;
    try {
      parsedFile = JSON.parse(previewText);
    } catch {
      bindingHandlers.writeError("Config is not valid JSON.");
      return;
    }

    if (!parsedFile || typeof parsedFile !== "object" || Array.isArray(parsedFile)) {
      bindingHandlers.writeError("Config must be a JSON object.");
      return;
    }

    const normalized = normalizeConfigPayload(parsedFile as Record<string, unknown>);
    const dataJson = JSON.stringify(normalized.data, null, 2);
    const wrappedPayload = buildWrappedPayload({
      data: normalized.data,
      version: normalized.version ?? bindings.version ?? undefined,
      savedAt: normalized.savedAt ?? undefined,
    });
    const wrappedJson = JSON.stringify(wrappedPayload, null, 2);
    loadedMetadataExtras = normalized.metadata ?? {};

    bindingHandlers.writeCurrentState(dataJson);
    bindingHandlers.writeBaselineState(dataJson);
    if (normalized.version) {
      bindingHandlers.writeVersion(normalized.version);
    }
    if (summaryName) {
      bindingHandlers.writeConfigFile(summaryName);
      bindingHandlers.writeConfigFileDisplay(extractFileName(summaryName) ?? summaryName);
    }

    bindingHandlers.writeSavedAt(normalized.savedAt ?? "");

    loadedConfigSummary = {
      name: summaryName,
      savedAt: normalized.savedAt ? formatSavedAt(normalized.savedAt) : undefined,
      version: normalized.version,
      rawText: dataJson,
      parsed: normalized.data,
      wrappedRawText: wrappedJson,
      wrappedParsed: wrappedPayload,
    };
    loadedConfigPath = summaryName;

    if (parsedFiles.length > 0) {
      bindingHandlers.removeFile(0);
    }

    bindingHandlers.writeError("");
    resetPreviewState();
    managerOpen = false;
    showLoadedPreview = false;
    previewFromLoaded = false;
  };

  // managerOpen
  $effect(() => {
    if (managerOpen) {
      showLoadedPreview = false;

      if (!previewFile && loadedConfigSummary?.rawText) {
        previewFromLoaded = true;
        previewText = loadedConfigSummary.rawText;
        previewFile = {
          name: loadedConfigSummary.name ?? "Loaded config",
          size: computeByteSize(loadedConfigSummary.rawText),
          type: "application/json",
        };
        previewJson = loadedConfigSummary.parsed;
      }
    } else if (previewFromLoaded) {
      resetPreviewState();
      previewFromLoaded = false;
    }
  });

  const isLoadedConfigCurrent = $derived.by(() => {
    if (!loadedConfigSummary?.rawText) return false;
    const candidate = normalizedPreviewData ?? previewText;
    if (!candidate) return false;
    return candidate.trim() === loadedConfigSummary.rawText.trim();
  });
</script>

<div class="space-y-6">
  {#if managerOpen}
    <div class="space-y-4 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p class="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Manage Configs
          </p>
          <p class="text-sm text-zinc-500 dark:text-zinc-400">
            Load a JSON config or prepare a notebook save.
          </p>
        </div>
        <Button variant="outline" onclick={() => (managerOpen = false)}>
          Close
        </Button>
      </div>

      <Tabs.Root bind:value={activeTab}>
        <Tabs.List>
          <Tabs.Trigger value="find">Browse Configs</Tabs.Trigger>
          <Tabs.Trigger value="save">Save Config</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="find">
          <BrowseConfigsPanel
            file={previewFile}
            rawContents={normalizedPreviewData ?? previewText}
            parsedContents={normalizedPreviewParsed}
            baselineContents={baselineParsed}
            savedAtLabel={previewSavedAt}
            versionLabel={previewVersion}
            dirty={isDirty}
            error={bindings.error}
            maxFiles={maxFiles}
            onUpload={handleUpload}
            onFileRejected={bindingHandlers.handleFileRejected}
            onRemove={handleRemove}
            onLoad={handleLoadConfig}
            disableLoad={isLoadedConfigCurrent}
            wrappedContents={previewWrappedJson ?? previewText}
            wrappedParsed={previewWrappedPayload ?? previewJson}
          />
        </Tabs.Content>

        <Tabs.Content value="save">
          <SaveConfigPanel
            bindings={bindings}
            rawConfig={bindings.current_state}
            baselineConfig={baselineParsed}
            defaultFileName={defaultSaveTarget}
            saveTargetLabel={defaultSaveLabel}
            dirty={isDirty}
            currentVersion={selectedConfigVersion}
            canEditVersion={canEditSelectedConfigVersion}
          />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  {:else if showLoadedPreview && loadedConfigSummary?.rawText}
    <LoadedConfigPreview
      fileName={loadedConfigSummary.name}
      savedAtLabel={loadedConfigSummary.savedAt}
      versionLabel={loadedConfigSummary.version}
      rawContents={loadedConfigSummary.rawText}
      parsedContents={loadedConfigSummary.parsed}
      baselineContents={baselineParsed}
      dirty={isDirty}
      onClose={() => (showLoadedPreview = false)}
      wrappedContents={loadedConfigSummary.wrappedRawText}
      wrappedParsed={loadedConfigSummary.wrappedParsed}
      onManage={() => {
        showLoadedPreview = false;
        managerOpen = true;
      }}
    />
  {:else}
    <div
      class="flex flex-col gap-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
    >
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div class="space-y-1">
          <p class="text-sm font-medium text-zinc-500 dark:text-zinc-400">
            Configuration
          </p>
          {#if loadedConfigSummary}
            <p class="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              {configFileDisplayName || loadedConfigSummary.name}
            </p>
            {#if loadedConfigSummary.savedAt || bindings.version}
              <div class="flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                {#if loadedConfigSummary.savedAt}
                  <span>Saved {loadedConfigSummary.savedAt}</span>
                {/if}
                {#if bindings.version}
                  <Badge variant="secondary" class="px-2 py-0.5 text-[0.65rem]">
                    {bindings.version}
                  </Badge>
                {/if}
                {#if isDirty}
                  <Badge variant="secondary" class="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-200">
                    Unsaved changes
                  </Badge>
                {/if}
              </div>
            {/if}
          {:else}
            <p class="text-base text-zinc-600 dark:text-zinc-300">
              No config loaded.
            </p>
          {/if}
        </div>

        <div class="flex gap-2">
          <Button variant="outline" onclick={() => (managerOpen = true)}>
            Manage Configs
          </Button>
{#if loadedConfigSummary?.rawText}
            <Button
              variant="outline"
              disabled={!loadedConfigSummary?.rawText}
              onclick={() => (showLoadedPreview = true)}
            >
              View Config
            </Button>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>

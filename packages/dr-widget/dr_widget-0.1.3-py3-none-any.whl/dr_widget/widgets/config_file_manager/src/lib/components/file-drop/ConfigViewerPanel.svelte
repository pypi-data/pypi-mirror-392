<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import SimpleJsonViewer from "./SimpleJsonViewer.svelte";
  import ComplexJsonViewer from "./ComplexJsonViewer.svelte";
  type ViewerMode = "simple" | "complex";
  type ViewerSource = "data" | "wrapped";

  const {
    data,
    rawJson,
    baselineData,
    dirty = false,
    initialMode = "simple",
    wrappedJson,
    wrappedData,
  } =
    $props<{
      data?: unknown;
      rawJson?: string;
      baselineData?: unknown;
      dirty?: boolean;
      initialMode?: ViewerMode;
      wrappedJson?: string;
      wrappedData?: unknown;
    }>();

  const complexModeEnabled = false;

  let mode = $state<ViewerMode>(complexModeEnabled ? initialMode : "simple");
  let source = $state<ViewerSource>("data");
  let copyState = $state<"idle" | "copied" | "error">("idle");
  const hasWrappedView = $derived.by(() => Boolean(wrappedJson || wrappedData));

  const switchMode = (nextMode: ViewerMode) => {
    if (!complexModeEnabled && nextMode === "complex") {
      mode = "simple";
      return;
    }
    mode = nextMode;
  };

  const switchSource = (nextSource: ViewerSource) => {
    if (!hasWrappedView) {
      source = "data";
      return;
    }
    source = nextSource;
  };

  $effect(() => {
    if (!hasWrappedView) {
      source = "data";
    }
  });

  const effectiveRawJson = $derived.by(() =>
    source === "data" ? rawJson : wrappedJson ?? rawJson,
  );
  const effectiveData = $derived.by(() =>
    source === "data" ? data : wrappedData ?? data,
  );
  const effectiveDirty = $derived.by(() => (source === "data" ? dirty : false));
  const effectiveBaseline = $derived.by(() =>
    source === "data" ? baselineData : undefined,
  );

  const copyToClipboard = async () => {
    const payload =
      effectiveRawJson ??
      (effectiveData !== undefined
        ? JSON.stringify(effectiveData, null, 2)
        : undefined);

    if (!payload) return;

    try {
      await navigator.clipboard.writeText(payload);
      copyState = "copied";
      setTimeout(() => {
        copyState = "idle";
      }, 1800);
    } catch {
      copyState = "error";
    }
  };
</script>

<Card.Root>
  <Card.Header>
    <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
      <div>
        <Card.Title>Config Preview</Card.Title>
        <Card.Description>
          Inspect the selected file in a formatted tree.
        </Card.Description>
        {#if hasWrappedView}
          <div class="mt-2 inline-flex rounded-md border border-zinc-200 bg-white p-0.5 text-xs dark:border-zinc-800 dark:bg-zinc-900">
            <button
              type="button"
              class="viewer-toggle"
              class:viewer-toggle-active={source === "data"}
              onclick={() => switchSource("data")}
            >
              Editable Data
            </button>
            <button
              type="button"
              class="viewer-toggle"
              class:viewer-toggle-active={source === "wrapped"}
              onclick={() => switchSource("wrapped")}
            >
              Saved Payload
            </button>
          </div>
        {/if}
      </div>

      <div class="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center">
        {#if complexModeEnabled}
          <div class="flex rounded-md border border-zinc-200 bg-white p-0.5 dark:border-zinc-800 dark:bg-zinc-900">
            <button
              type="button"
              class="viewer-toggle"
              class:viewer-toggle-active={mode === "simple"}
              onclick={() => switchMode("simple")}
            >
              Simple
            </button>
            <button
              type="button"
              class="viewer-toggle"
              class:viewer-toggle-active={mode === "complex"}
              onclick={() => switchMode("complex")}
            >
              Complex
            </button>
          </div>
        {/if}

        <Button
          variant="outline"
          size="sm"
          onclick={copyToClipboard}
          disabled={effectiveData === undefined && !effectiveRawJson}
        >
          {copyState === "copied" ? "Copied!" : "Copy JSON"}
        </Button>
      </div>
    </div>

    {#if copyState === "error"}
      <p class="text-xs font-medium text-red-500">
        Clipboard copy failed. Try copying manually.
      </p>
    {/if}
  </Card.Header>

  <Card.Content class="space-y-4">
    {#if mode === "simple" || !complexModeEnabled}
      <div
        class="viewer-shell rounded-xl border border-zinc-100 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
      >
        <SimpleJsonViewer
          data={effectiveData}
          baseline={effectiveDirty ? effectiveBaseline : undefined}
          dirty={effectiveDirty}
          depth={3}
          preserveKeyOrder={source === "wrapped"}
        />
      </div>
    {:else}
      <div
        class="rounded-xl border border-zinc-100 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
      >
        <ComplexJsonViewer data={effectiveData} />
      </div>
    {/if}

    {#if effectiveDirty && effectiveBaseline}
      <div class="diff-legend" role="note">
        <span class="legend-item">
          <span class="legend-swatch legend-swatch-added"></span>
          New value
        </span>
        <span class="legend-item">
          <span class="legend-swatch legend-swatch-removed"></span>
          Removed value
        </span>
      </div>
    {/if}

  </Card.Content>
</Card.Root>

<style>
  .viewer-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 0.45rem;
    color: #3f3f46;
    transition: all 0.15s ease;
  }

  .viewer-toggle:hover {
    background-color: rgba(37, 99, 235, 0.08);
  }

  .viewer-toggle-active {
    background-color: #2563eb;
    color: white;
    box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.15);
  }

  :global(.dark) .viewer-toggle {
    color: #d4d4d8;
  }

  :global(.dark) .viewer-toggle:hover {
    background-color: rgba(37, 99, 235, 0.2);
  }

  .viewer-shell {
    max-height: 22rem;
    overflow: auto;
    padding: 1.25rem;
    font-family: ui-monospace, SFMono-Regular, SFMono, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
    font-size: 0.75rem;
    line-height: 1.4;
    color: #3f3f46;
  }

  .diff-legend {
    display: flex;
    gap: 1rem;
    align-items: center;
    font-size: 0.7rem;
    color: #71717a;
  }

  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  .legend-swatch {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 0.25rem;
  }

  .legend-swatch-added {
    background: rgba(34, 197, 94, 0.2);
  }

  .legend-swatch-removed {
    background: rgba(239, 68, 68, 0.25);
  }

  :global(.dark) .viewer-shell {
    color: #e4e4e7;
    background: rgba(24, 24, 27, 0.8);
  }

  :global(.dark) .diff-legend {
    color: #a1a1aa;
  }

  :global(.dark) .legend-swatch-added {
    background: rgba(34, 197, 94, 0.3);
  }

  :global(.dark) .legend-swatch-removed {
    background: rgba(239, 68, 68, 0.35);
  }
</style>

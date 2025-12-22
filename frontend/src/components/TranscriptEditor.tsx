import { Fragment, useEffect, useMemo, useRef, useState } from 'react'

import {
  redoEdit,
  submitEditOperation,
  undoEdit,
  type EditOperationPayload,
  type Transcript,
  type TranscriptToken,
} from '@/services/projects'

type WordNode = {
  id: string
  tokenIds: string[]
  wordText: string
  punctuationTokens: Array<{ id: string; text: string }>
  start: number | null
  end: number | null
  kind: 'original' | 'inserted' | 'deleted' | 'replaced'
  origin: 'insert' | 'replace' | null
}

type EditorSnapshot = {
  words: WordNode[]
  cursorIndex: number
  selection: SelectionRange | null
  draft: string
  pendingReplaceTokens: string[] | null
  operations: EditOperationPayload[]
}

type SelectionRange = {
  start: number
  end: number
}

function isPrintableKey(event: React.KeyboardEvent): boolean {
  if (event.ctrlKey || event.metaKey || event.altKey) return false
  return event.key.length === 1
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

function uuidV4(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  const bytes = new Uint8Array(16)
  crypto.getRandomValues(bytes)
  bytes[6] = (bytes[6] & 0x0f) | 0x40
  bytes[8] = (bytes[8] & 0x3f) | 0x80
  const hex = Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('')
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

function normalizeInsertedText(text: string): string {
  return text.replace(/\s+/g, ' ').trim()
}

function tokensToWords(tokens: TranscriptToken[]): WordNode[] {
  const words: WordNode[] = []
  let lastWord: WordNode | null = null
  for (const token of tokens) {
    if (token.type === 'word') {
      const kind: WordNode['kind'] =
        token.status === 'deleted'
          ? 'deleted'
          : token.status === 'replaced'
            ? 'replaced'
            : token.status === 'inserted' || token.status === 'generated'
              ? 'inserted'
              : 'original'
      lastWord = {
        id: token.id,
        tokenIds: [token.id],
        wordText: token.text,
        punctuationTokens: [],
        start: token.start,
        end: token.end,
        kind,
        origin: null,
      }
      words.push(lastWord)
      continue
    }
    if (token.type === 'punctuation') {
      if (!lastWord) continue
      lastWord.punctuationTokens.push({ id: token.id, text: token.text })
      lastWord.tokenIds.push(token.id)
    }
  }
  return words
}

function selectionToOldTokens(
  words: WordNode[],
  selection: SelectionRange | null
): string[] {
  if (!selection) return []
  const start = Math.min(selection.start, selection.end)
  const end = Math.max(selection.start, selection.end)
  const ids: string[] = []
  for (let index = start; index <= end; index += 1) {
    const node = words[index]
    if (!node) continue
    if (node.kind !== 'original') continue
    ids.push(...node.tokenIds)
  }
  return ids
}

function computeCharOffset(words: WordNode[], cursorIndex: number): number {
  const safe = clamp(cursorIndex, 0, words.length)
  let offset = 0
  let activeCount = 0
  for (let index = 0; index < safe; index += 1) {
    const word = words[index]
    if (word.kind === 'deleted' || word.kind === 'replaced') continue
    if (activeCount > 0) offset += 1
    offset +=
      `${word.wordText}${word.punctuationTokens.map((t) => t.text).join('')}`
        .length
    activeCount += 1
  }
  return offset
}

function getTokenAtCursor(
  words: WordNode[],
  cursorIndex: number
): WordNode | null {
  if (words.length === 0) return null
  if (cursorIndex <= 0) return null
  for (
    let index = clamp(cursorIndex - 1, 0, words.length - 1);
    index >= 0;
    index -= 1
  ) {
    const candidate = words[index]
    if (!candidate) continue
    if (candidate.kind === 'deleted' || candidate.kind === 'replaced') continue
    if (candidate.kind !== 'original') return null
    return candidate
  }
  return null
}

function findPreviousEditableIndex(
  words: WordNode[],
  cursorIndex: number
): number | null {
  for (
    let index = clamp(cursorIndex - 1, 0, words.length - 1);
    index >= 0;
    index -= 1
  ) {
    const node = words[index]
    if (!node) continue
    if (node.kind === 'original' || node.kind === 'inserted') return index
  }
  return null
}

function getTokensInSelection(
  words: WordNode[],
  selection: SelectionRange | null
): WordNode[] {
  if (!selection) return []
  const start = Math.min(selection.start, selection.end)
  const end = Math.max(selection.start, selection.end)
  const selected: WordNode[] = []
  for (let index = start; index <= end; index += 1) {
    const node = words[index]
    if (!node) continue
    if (node.kind === 'inserted') continue
    selected.push(node)
  }
  return selected
}

function selectionToText(
  words: WordNode[],
  selection: SelectionRange | null
): string {
  if (!selection) return ''
  const start = Math.min(selection.start, selection.end)
  const end = Math.max(selection.start, selection.end)
  return words
    .slice(start, end + 1)
    .filter((w) => w.kind !== 'deleted' && w.kind !== 'replaced')
    .map(
      (w) => `${w.wordText}${w.punctuationTokens.map((t) => t.text).join('')}`
    )
    .join(' ')
}

export function TranscriptEditor({
  transcript,
  projectId,
  onOperationsChange,
}: {
  transcript: Transcript
  projectId?: string
  onOperationsChange?: (operations: EditOperationPayload[]) => void
}): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const previewAudioRef = useRef<HTMLAudioElement | null>(null)

  const initialWords = useMemo(
    () => tokensToWords(transcript.tokens),
    [transcript]
  )

  const [words, setWords] = useState<WordNode[]>(() => initialWords)
  const [cursorIndex, setCursorIndex] = useState<number>(
    () => initialWords.length
  )
  const [selection, setSelection] = useState<SelectionRange | null>(null)
  const [draft, setDraft] = useState<string>('')
  const [pendingReplaceTokens, setPendingReplaceTokens] = useState<
    string[] | null
  >(null)
  const [operations, setOperations] = useState<EditOperationPayload[]>([])
  const [undoStack, setUndoStack] = useState<EditorSnapshot[]>([])
  const [redoStack, setRedoStack] = useState<EditorSnapshot[]>([])
  const [backendStatus, setBackendStatus] = useState<{
    status: 'idle' | 'syncing' | 'ok' | 'error'
    detail: string | null
  }>({ status: 'idle', detail: null })
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewStatus, setPreviewStatus] = useState<{
    status: 'idle' | 'loading' | 'error'
    detail: string | null
  }>({ status: 'idle', detail: null })

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  useEffect(() => {
    onOperationsChange?.(operations)
  }, [operations, onOperationsChange])

  function recordOperation(next: EditOperationPayload): EditOperationPayload {
    const last = operations.at(-1)
    if (
      last &&
      last.type === 'insert' &&
      next.type === 'insert' &&
      last.old_tokens.length === 0 &&
      next.old_tokens.length === 0
    ) {
      const lastTime = Date.parse(last.timestamp)
      const nextTime = Date.parse(next.timestamp)
      const withinWindow =
        Number.isFinite(lastTime) &&
        Number.isFinite(nextTime) &&
        nextTime - lastTime < 900
      const expectedNext =
        last.position + (last.new_text ? last.new_text.length + 1 : 0)

      if (withinWindow && next.position === expectedNext) {
        const merged: EditOperationPayload = {
          ...last,
          new_text: last.new_text
            ? `${last.new_text} ${next.new_text}`
            : next.new_text,
          timestamp: next.timestamp,
        }
        setOperations((prev) => [...prev.slice(0, -1), merged])
        return merged
      }
    }

    setOperations((prev) => [...prev, next])
    return next
  }

  async function syncOperation(operation: EditOperationPayload): Promise<void> {
    if (!projectId) return
    setBackendStatus({
      status: 'syncing',
      detail: `${operation.type} ${operation.id}`,
    })
    try {
      await submitEditOperation(projectId, operation)
      setBackendStatus({
        status: 'ok',
        detail: `${operation.type} ${operation.id}`,
      })
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to sync edit'
      setBackendStatus({ status: 'error', detail: message })
    }
  }

  async function syncUndo(): Promise<void> {
    if (!projectId) return
    setBackendStatus({ status: 'syncing', detail: 'undo' })
    try {
      await undoEdit(projectId)
      setBackendStatus({ status: 'ok', detail: 'undo' })
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to sync undo'
      setBackendStatus({ status: 'error', detail: message })
    }
  }

  async function syncRedo(): Promise<void> {
    if (!projectId) return
    setBackendStatus({ status: 'syncing', detail: 'redo' })
    try {
      await redoEdit(projectId)
      setBackendStatus({ status: 'ok', detail: 'redo' })
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to sync redo'
      setBackendStatus({ status: 'error', detail: message })
    }
  }

  const selectedOldTokens = useMemo(
    () => selectionToOldTokens(words, selection),
    [selection, words]
  )
  const selectedTokens = useMemo(
    () => getTokensInSelection(words, selection),
    [selection, words]
  )

  const tokenAtCursor = useMemo(() => {
    return getTokenAtCursor(words, cursorIndex)
  }, [cursorIndex, words])

  function focusEditor(): void {
    containerRef.current?.focus()
  }

  function clearSelection(): void {
    setSelection(null)
  }

  function snapshot(): EditorSnapshot {
    return {
      words: [...words],
      cursorIndex,
      selection: selection ? { ...selection } : null,
      draft,
      pendingReplaceTokens: pendingReplaceTokens
        ? [...pendingReplaceTokens]
        : null,
      operations: [...operations],
    }
  }

  function pushUndo(): void {
    const current = snapshot()
    setUndoStack((prev) => [...prev.slice(-49), current])
    setRedoStack([])
  }

  function restore(state: EditorSnapshot): void {
    setWords(state.words)
    setCursorIndex(state.cursorIndex)
    setSelection(state.selection)
    setDraft(state.draft)
    setPendingReplaceTokens(state.pendingReplaceTokens)
    setOperations(state.operations)
  }

  function undo(): void {
    setUndoStack((prevUndo) => {
      const last = prevUndo.at(-1)
      if (!last) return prevUndo
      setRedoStack((prevRedo) => [...prevRedo, snapshot()])
      restore(last)
      return prevUndo.slice(0, -1)
    })
  }

  function redo(): void {
    setRedoStack((prevRedo) => {
      const last = prevRedo.at(-1)
      if (!last) return prevRedo
      setUndoStack((prevUndo) => [...prevUndo, snapshot()])
      restore(last)
      return prevRedo.slice(0, -1)
    })
  }

  function deleteRange(range: SelectionRange): void {
    pushUndo()
    const start = Math.min(range.start, range.end)
    const end = Math.max(range.start, range.end)
    const oldTokens = selectionToOldTokens(words, range)
    const position = computeCharOffset(words, start)

    setWords((prev) =>
      prev.map((node, index) => {
        if (index < start || index > end) return node
        if (node.kind === 'deleted' || node.kind === 'replaced') return node
        return { ...node, kind: 'deleted' }
      })
    )
    setCursorIndex(start)
    clearSelection()

    const op: EditOperationPayload = {
      id: uuidV4(),
      type: 'delete',
      position,
      old_tokens: oldTokens,
      new_text: '',
      timestamp: new Date().toISOString(),
    }
    const recorded = recordOperation(op)
    void syncOperation(recorded)
  }

  function applyInsertionText(
    raw: string,
    replaceRange: SelectionRange | null = null
  ): void {
    const normalized = normalizeInsertedText(raw)
    if (!normalized) return

    const insertWords = normalized.split(' ').filter(Boolean)
    if (insertWords.length === 0) return

    pushUndo()

    const range = replaceRange
    const start = range ? Math.min(range.start, range.end) : cursorIndex
    const end = range ? Math.max(range.start, range.end) : start - 1
    const oldTokens = range
      ? selectionToOldTokens(words, range)
      : (pendingReplaceTokens ?? [])
    const type: EditOperationPayload['type'] =
      range || (pendingReplaceTokens && pendingReplaceTokens.length > 0)
        ? 'replace'
        : 'insert'
    const position = computeCharOffset(words, start)

    const inserted: WordNode[] = insertWords.map((word, index) => ({
      id: `ins-${Date.now()}-${start}-${index}`,
      tokenIds: [],
      wordText: word,
      punctuationTokens: [],
      start: null,
      end: null,
      kind: 'inserted',
      origin: type,
    }))

    const nextWords: WordNode[] = []
    if (range) {
      for (let index = 0; index < words.length; index += 1) {
        if (index === start) {
          nextWords.push(...inserted)
        }
        const node = words[index]
        if (index >= start && index <= end) {
          if (node.kind === 'original') {
            nextWords.push({ ...node, kind: 'replaced' })
            continue
          }
          if (node.kind === 'inserted') {
            nextWords.push({ ...node, kind: 'deleted' })
            continue
          }
          nextWords.push(node)
          continue
        }
        nextWords.push(node)
      }
    } else {
      nextWords.push(...words.slice(0, cursorIndex))
      nextWords.push(...inserted)
      nextWords.push(...words.slice(cursorIndex))
    }

    setWords(nextWords)
    setCursorIndex(start + inserted.length)
    setDraft('')
    setPendingReplaceTokens(null)
    clearSelection()

    const op: EditOperationPayload = {
      id: uuidV4(),
      type,
      position,
      old_tokens: oldTokens,
      new_text: normalized,
      timestamp: new Date().toISOString(),
    }
    const recorded = recordOperation(op)
    void syncOperation(recorded)
  }

  function commitDraft(): void {
    if (!draft.trim()) return
    applyInsertionText(draft)
  }

  function startReplaceIfSelected(): void {
    if (!selection) return
    pushUndo()
    const start = Math.min(selection.start, selection.end)
    const end = Math.max(selection.start, selection.end)
    const oldTokens = selectionToOldTokens(words, selection)
    setPendingReplaceTokens(oldTokens)
    setWords((prev) =>
      prev.map((node, index) => {
        if (index < start || index > end) return node
        if (node.kind === 'original') return { ...node, kind: 'replaced' }
        if (node.kind === 'inserted') return { ...node, kind: 'deleted' }
        return node
      })
    )
    setCursorIndex(start)
    clearSelection()
  }

  function onKeyDown(event: React.KeyboardEvent<HTMLDivElement>): void {
    const modifier = event.ctrlKey || event.metaKey
    if (modifier && event.key.toLowerCase() === 'a') {
      event.preventDefault()
      if (words.length > 0) {
        setSelection({ start: 0, end: words.length - 1 })
        setCursorIndex(words.length)
      }
      return
    }
    if (modifier && event.key.toLowerCase() === 'c') {
      if (!selection) return
      event.preventDefault()
      const text = selectionToText(words, selection)
      void navigator.clipboard.writeText(text).catch(() => {})
      return
    }
    if (modifier && event.key.toLowerCase() === 'x') {
      if (!selection) return
      event.preventDefault()
      const text = selectionToText(words, selection)
      void navigator.clipboard.writeText(text).catch(() => {})
      deleteRange(selection)
      return
    }
    if (modifier && event.key.toLowerCase() === 'z') {
      event.preventDefault()
      if (event.shiftKey) {
        redo()
        void syncRedo()
      } else {
        undo()
        void syncUndo()
      }
      return
    }

    if (event.key === ' ') {
      event.preventDefault()
      commitDraft()
      return
    }

    if (event.key === 'Backspace') {
      event.preventDefault()
      if (draft) {
        setDraft('')
        return
      }
      if (selection) {
        deleteRange(selection)
        return
      }
      const previousIndex = findPreviousEditableIndex(words, cursorIndex)
      if (previousIndex == null) return
      deleteRange({ start: previousIndex, end: previousIndex })
      return
    }

    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault()
      commitDraft()
      const delta = event.key === 'ArrowLeft' ? -1 : 1
      const next = clamp(cursorIndex + delta, 0, words.length)
      setCursorIndex(next)
      if (event.shiftKey) {
        setSelection((prev) => {
          if (words.length === 0) return null
          if (!prev) {
            const initial =
              delta < 0
                ? clamp(cursorIndex - 1, 0, words.length - 1)
                : clamp(cursorIndex, 0, words.length - 1)
            return { start: initial, end: initial }
          }
          const nextEnd = clamp(prev.end + delta, 0, words.length - 1)
          return { start: prev.start, end: nextEnd }
        })
      } else {
        clearSelection()
      }
      return
    }

    if (event.key === 'Escape') {
      event.preventDefault()
      if (pendingReplaceTokens) {
        undo()
        return
      }
      setDraft('')
      setPendingReplaceTokens(null)
      clearSelection()
      return
    }

    if (isPrintableKey(event)) {
      event.preventDefault()
      if (selection) startReplaceIfSelected()
      setDraft((prev) => `${prev}${event.key}`)
    }
  }

  function isSelected(index: number): boolean {
    if (!selection) return false
    const start = Math.min(selection.start, selection.end)
    const end = Math.max(selection.start, selection.end)
    return index >= start && index <= end
  }

  function onWordMouseDown(index: number, event: React.MouseEvent): void {
    event.preventDefault()
    commitDraft()
    if (event.shiftKey && selection) {
      setSelection({ start: selection.start, end: index })
    } else {
      setSelection({ start: index, end: index })
    }
    setCursorIndex(index + 1)
    focusEditor()
  }

  const debugText = useMemo(() => {
    const text = words
      .filter((w) => w.kind !== 'deleted' && w.kind !== 'replaced')
      .map(
        (w) => `${w.wordText}${w.punctuationTokens.map((t) => t.text).join('')}`
      )
      .join(' ')
    return text
  }, [words])

  return (
    <div style={{ maxWidth: 900, margin: '24px auto 0' }}>
      <h2>Transcript editor</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <button
          type="button"
          disabled={undoStack.length === 0}
          onClick={() => {
            undo()
            void syncUndo()
            focusEditor()
          }}
        >
          Undo
        </button>
        <button
          type="button"
          disabled={redoStack.length === 0}
          onClick={() => {
            redo()
            void syncRedo()
            focusEditor()
          }}
        >
          Redo
        </button>
        <button
          type="button"
          disabled={!projectId || previewStatus.status === 'loading'}
          onClick={async () => {
            if (!projectId) return
            setPreviewStatus({ status: 'loading', detail: null })
            try {
              const response = await fetch(`/api/projects/${projectId}/preview`)
              if (!response.ok) {
                throw new Error(`Preview failed (${response.status})`)
              }
              const blob = await response.blob()
              const nextUrl = URL.createObjectURL(blob)
              setPreviewUrl((prev) => {
                if (prev) URL.revokeObjectURL(prev)
                return nextUrl
              })
              setPreviewStatus({ status: 'idle', detail: null })
              setTimeout(() => {
                void previewAudioRef.current?.play().catch(() => {})
              }, 0)
            } catch (error) {
              const message =
                error instanceof Error ? error.message : 'Preview failed'
              setPreviewStatus({ status: 'error', detail: message })
            }
          }}
        >
          {previewStatus.status === 'loading'
            ? 'Rendering Preview...'
            : 'Preview Edited Audio'}
        </button>
      </div>
      {previewStatus.status === 'error' && previewStatus.detail && (
        <div style={{ color: '#b71c1c', marginBottom: 12 }}>
          {previewStatus.detail}
        </div>
      )}
      {previewUrl && (
        <div style={{ marginBottom: 12 }}>
          <audio ref={previewAudioRef} controls src={previewUrl} />
        </div>
      )}
      <div
        ref={containerRef}
        tabIndex={0}
        onKeyDown={onKeyDown}
        onPaste={(event) => {
          event.preventDefault()
          const text = event.clipboardData.getData('text/plain')
          if (!text) return
          const combined = draft ? `${draft} ${text}` : text
          if (selection) {
            applyInsertionText(combined, selection)
          } else {
            applyInsertionText(combined)
          }
        }}
        onDrop={(event) => {
          event.preventDefault()
          const text = event.dataTransfer.getData('text/plain')
          if (!text) return
          const combined = draft ? `${draft} ${text}` : text
          if (selection) {
            applyInsertionText(combined, selection)
          } else {
            applyInsertionText(combined)
          }
        }}
        onDragOver={(event) => {
          event.preventDefault()
        }}
        style={{
          padding: 12,
          border: '1px solid #ddd',
          borderRadius: 12,
          minHeight: 96,
          outline: 'none',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 8,
            alignItems: 'center',
          }}
        >
          {words.map((word, index) => (
            <Fragment key={word.id}>
              {index === cursorIndex && (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: '6px 10px',
                    borderRadius: 999,
                    border: '1px dashed #bbb',
                    background: draft ? 'rgba(27,94,32,0.08)' : 'transparent',
                    color: draft ? '#1b5e20' : '#999',
                    minWidth: 24,
                    userSelect: 'none',
                  }}
                  title="Type to insert a word; press Space to commit"
                  onMouseDown={(event) => {
                    event.preventDefault()
                    focusEditor()
                  }}
                >
                  {draft || '|'}
                </span>
              )}
              <span
                data-token-id={word.tokenIds[0] ?? undefined}
                onMouseDown={(event) => onWordMouseDown(index, event)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '6px 10px',
                  borderRadius: 999,
                  border:
                    word.kind === 'deleted' || word.kind === 'replaced'
                      ? '1px dashed #bbb'
                      : word.kind === 'inserted'
                        ? `1px solid ${
                            word.origin === 'replace' ? '#d1a93a' : '#2e7d32'
                          }`
                        : '1px solid #cfcfcf',
                  background: isSelected(index)
                    ? 'rgba(100,108,255,0.16)'
                    : word.kind === 'deleted'
                      ? 'rgba(0,0,0,0.04)'
                      : word.kind === 'replaced'
                        ? 'rgba(255,193,7,0.12)'
                        : word.kind === 'inserted'
                          ? word.origin === 'replace'
                            ? 'rgba(255,193,7,0.18)'
                            : 'rgba(27,94,32,0.12)'
                          : '#fff',
                  userSelect: 'none',
                  cursor:
                    word.kind === 'deleted' || word.kind === 'replaced'
                      ? 'default'
                      : 'pointer',
                  fontWeight: word.kind === 'inserted' ? 700 : 500,
                  textDecoration:
                    word.kind === 'deleted' || word.kind === 'replaced'
                      ? 'line-through'
                      : 'none',
                  color:
                    word.kind === 'deleted'
                      ? '#666'
                      : word.kind === 'replaced'
                        ? '#8a6d3b'
                        : 'inherit',
                }}
                title={
                  word.start != null && word.end != null
                    ? `${word.kind.toUpperCase()} ${word.start.toFixed(2)}s–${word.end.toFixed(2)}s`
                    : word.kind === 'inserted'
                      ? word.origin === 'replace'
                        ? 'Inserted replacement (no timestamps)'
                        : 'Inserted word (no timestamps)'
                      : 'No timestamps'
                }
              >
                {word.tokenIds.length > 0 ? (
                  <>
                    <span data-token-id={word.tokenIds[0]}>
                      {word.wordText}
                    </span>
                    {word.punctuationTokens.map((token) => (
                      <span key={token.id} data-token-id={token.id}>
                        {token.text}
                      </span>
                    ))}
                    {word.kind === 'inserted' && (
                      <span
                        style={{
                          marginLeft: 6,
                          padding: '2px 6px',
                          borderRadius: 999,
                          fontSize: 10,
                          fontWeight: 700,
                          color: '#0d47a1',
                          background: 'rgba(25,118,210,0.12)',
                          border: '1px solid rgba(25,118,210,0.28)',
                        }}
                      >
                        GEN
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    <span>{word.wordText}</span>
                    {word.kind === 'inserted' && (
                      <span
                        style={{
                          marginLeft: 6,
                          padding: '2px 6px',
                          borderRadius: 999,
                          fontSize: 10,
                          fontWeight: 700,
                          color: '#0d47a1',
                          background: 'rgba(25,118,210,0.12)',
                          border: '1px solid rgba(25,118,210,0.28)',
                        }}
                      >
                        GEN
                      </span>
                    )}
                  </>
                )}
              </span>
            </Fragment>
          ))}
          {cursorIndex === words.length && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '6px 10px',
                borderRadius: 999,
                border: '1px dashed #bbb',
                background: draft ? 'rgba(27,94,32,0.08)' : 'transparent',
                color: draft ? '#1b5e20' : '#999',
                minWidth: 24,
                userSelect: 'none',
              }}
              title="Type to insert a word; press Space to commit"
              onMouseDown={(event) => {
                event.preventDefault()
                focusEditor()
              }}
            >
              {draft || '|'}
            </span>
          )}
        </div>
      </div>

      <div
        style={{
          marginTop: 16,
          padding: 12,
          borderRadius: 12,
          background: '#fafafa',
        }}
      >
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Debug</div>
        <div
          style={{
            fontSize: 12,
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
          }}
        >
          <div>cursorIndex: {cursorIndex}</div>
          <div>charOffset: {computeCharOffset(words, cursorIndex)}</div>
          <div>
            tokenAtCursor:{' '}
            {tokenAtCursor?.tokenIds?.[0]
              ? `${tokenAtCursor.tokenIds[0]} (${tokenAtCursor.start?.toFixed(2)}–${tokenAtCursor.end?.toFixed(2)}s)`
              : 'null'}
          </div>
          <div>
            selection:{' '}
            {selection ? `${selection.start}..${selection.end}` : 'none'}{' '}
            (old_tokens:{' '}
            {selectedOldTokens.length ? selectedOldTokens.join(', ') : 'none'})
          </div>
          <div>
            selectedTokens:{' '}
            {selectedTokens.length
              ? selectedTokens
                  .map(
                    (token) => `${token.tokenIds[0]}@${token.start?.toFixed(2)}`
                  )
                  .join(' ')
              : 'none'}
          </div>
          <div>draft: {draft ? JSON.stringify(draft) : '""'}</div>
          <div>
            pendingReplaceTokens: {pendingReplaceTokens?.join(', ') ?? 'null'}
          </div>
          <div>
            undoStack: {undoStack.length} redoStack: {redoStack.length}
          </div>
          <div>
            backendSync: {backendStatus.status}
            {backendStatus.detail ? ` (${backendStatus.detail})` : ''}
          </div>
          <div style={{ marginTop: 8 }}>text: {JSON.stringify(debugText)}</div>
          <div style={{ marginTop: 8, fontWeight: 700 }}>last operations</div>
          {operations.slice(-5).map((op) => (
            <div key={`${op.timestamp}-${op.type}`}>
              {op.timestamp} {op.type} pos={op.position} old=[
              {op.old_tokens.join(',')}] new=
              {JSON.stringify(op.new_text)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

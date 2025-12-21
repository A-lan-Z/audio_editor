import { Fragment, useEffect, useMemo, useRef, useState } from 'react'

import type { Transcript, TranscriptToken } from '@/services/projects'

type WordNode = {
  id: string
  tokenIds: string[]
  wordText: string
  punctuationTokens: Array<{ id: string; text: string }>
  start: number | null
  end: number | null
  kind: 'original' | 'inserted'
}

type EditOperation = {
  type: 'insert' | 'delete' | 'replace'
  position: number
  old_tokens: string[]
  new_text: string
  timestamp: string
}

type EditorSnapshot = {
  words: WordNode[]
  cursorIndex: number
  selection: SelectionRange | null
  draft: string
  pendingReplaceTokens: string[] | null
  operations: EditOperation[]
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

function tokensToWords(tokens: TranscriptToken[]): WordNode[] {
  const words: WordNode[] = []
  let lastWord: WordNode | null = null
  for (const token of tokens) {
    if (token.type === 'word') {
      lastWord = {
        id: token.id,
        tokenIds: [token.id],
        wordText: token.text,
        punctuationTokens: [],
        start: token.start,
        end: token.end,
        kind: 'original',
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
    if (node.kind === 'inserted') continue
    ids.push(...node.tokenIds)
  }
  return ids
}

function computeCharOffset(words: WordNode[], cursorIndex: number): number {
  const safe = clamp(cursorIndex, 0, words.length)
  let offset = 0
  for (let index = 0; index < safe; index += 1) {
    const word = words[index]
    if (index > 0) offset += 1
    offset +=
      `${word.wordText}${word.punctuationTokens.map((t) => t.text).join('')}`
        .length
  }
  return offset
}

function getTokenAtCursor(
  words: WordNode[],
  cursorIndex: number
): WordNode | null {
  if (words.length === 0) return null
  if (cursorIndex <= 0) return null
  const candidate = words[clamp(cursorIndex - 1, 0, words.length - 1)]
  if (!candidate || candidate.kind === 'inserted') return null
  return candidate
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

export function TranscriptEditor({
  transcript,
  onOperationsChange,
}: {
  transcript: Transcript
  onOperationsChange?: (operations: EditOperation[]) => void
}): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null)

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
  const [operations, setOperations] = useState<EditOperation[]>([])
  const [undoStack, setUndoStack] = useState<EditorSnapshot[]>([])
  const [redoStack, setRedoStack] = useState<EditorSnapshot[]>([])

  useEffect(() => {
    onOperationsChange?.(operations)
  }, [operations, onOperationsChange])

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

    setWords((prev) => prev.filter((_, index) => index < start || index > end))
    setCursorIndex(start)
    clearSelection()

    const position = computeCharOffset(words, start)
    setOperations((prev) => [
      ...prev,
      {
        type: 'delete',
        position,
        old_tokens: oldTokens,
        new_text: '',
        timestamp: new Date().toISOString(),
      },
    ])
  }

  function commitDraft(): void {
    const text = draft.trim()
    if (!text) return
    pushUndo()

    const insertWords = text.split(/\s+/).filter(Boolean)
    if (insertWords.length === 0) return

    const position = computeCharOffset(words, cursorIndex)
    const oldTokens = pendingReplaceTokens ?? []
    const type: EditOperation['type'] =
      pendingReplaceTokens && pendingReplaceTokens.length > 0
        ? 'replace'
        : 'insert'

    const inserted: WordNode[] = insertWords.map((word, index) => ({
      id: `ins-${Date.now()}-${cursorIndex}-${index}`,
      tokenIds: [],
      wordText: word,
      punctuationTokens: [],
      start: null,
      end: null,
      kind: 'inserted',
    }))

    setWords((prev) => [
      ...prev.slice(0, cursorIndex),
      ...inserted,
      ...prev.slice(cursorIndex),
    ])
    setCursorIndex((prev) => prev + inserted.length)
    setDraft('')
    setPendingReplaceTokens(null)
    clearSelection()

    setOperations((prev) => [
      ...prev,
      {
        type,
        position,
        old_tokens: oldTokens,
        new_text: insertWords.join(' '),
        timestamp: new Date().toISOString(),
      },
    ])
  }

  function startReplaceIfSelected(): void {
    if (!selection) return
    pushUndo()
    const start = Math.min(selection.start, selection.end)
    const end = Math.max(selection.start, selection.end)
    const oldTokens = selectionToOldTokens(words, selection)
    setPendingReplaceTokens(oldTokens)
    setWords((prev) => prev.filter((_, index) => index < start || index > end))
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
    if (modifier && event.key.toLowerCase() === 'z') {
      event.preventDefault()
      if (event.shiftKey) {
        redo()
      } else {
        undo()
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
      if (cursorIndex <= 0) return
      deleteRange({ start: cursorIndex - 1, end: cursorIndex - 1 })
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
      .map(
        (w) => `${w.wordText}${w.punctuationTokens.map((t) => t.text).join('')}`
      )
      .join(' ')
    return text
  }, [words])

  return (
    <div style={{ maxWidth: 900, margin: '24px auto 0' }}>
      <h2>Transcript editor</h2>
      <div
        ref={containerRef}
        tabIndex={0}
        onKeyDown={onKeyDown}
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
                  border: '1px solid #cfcfcf',
                  background: isSelected(index)
                    ? 'rgba(100,108,255,0.16)'
                    : '#fff',
                  userSelect: 'none',
                  cursor: 'pointer',
                  fontWeight: word.kind === 'inserted' ? 700 : 500,
                }}
                title={
                  word.start != null && word.end != null
                    ? `${word.start.toFixed(2)}s–${word.end.toFixed(2)}s`
                    : 'Inserted word (no timestamps)'
                }
              >
                {word.kind === 'original' ? (
                  <>
                    <span data-token-id={word.tokenIds[0]}>
                      {word.wordText}
                    </span>
                    {word.punctuationTokens.map((token) => (
                      <span key={token.id} data-token-id={token.id}>
                        {token.text}
                      </span>
                    ))}
                  </>
                ) : (
                  <span>{word.wordText}</span>
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

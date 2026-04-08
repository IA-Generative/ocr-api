import { ref } from 'vue'
import type { components } from '@/api/types/api.schema'

type Bbox = components['schemas']['Bbox']

interface Point {
  x: number
  y: number
}

export interface DrawnBox extends Bbox {
  isDrawn: true
}

export function useBoxDrawing (onDrawn: (box: DrawnBox) => void) {
  const isDrawing = ref(false)
  const startPoint = ref<Point | null>(null)
  const previewRect = ref<{ x: number, y: number, w: number, h: number } | null>(null)

  function getRelativePoint (e: MouseEvent, el: HTMLElement): Point {
    const rect = el.getBoundingClientRect()
    return {
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height,
    }
  }

  function onMouseDown (e: MouseEvent, el: HTMLElement) {
    e.preventDefault()
    startPoint.value = getRelativePoint(e, el)
    isDrawing.value = true
    previewRect.value = null
  }

  function onMouseMove (e: MouseEvent, el: HTMLElement) {
    if (!isDrawing.value || !startPoint.value) return
    const current = getRelativePoint(e, el)
    previewRect.value = {
      x: Math.min(startPoint.value.x, current.x),
      y: Math.min(startPoint.value.y, current.y),
      w: Math.abs(current.x - startPoint.value.x),
      h: Math.abs(current.y - startPoint.value.y),
    }
  }

  function onMouseUp (e: MouseEvent, el: HTMLElement) {
    if (!isDrawing.value || !startPoint.value) return
    const current = getRelativePoint(e, el)

    const x = Math.min(startPoint.value.x, current.x)
    const y = Math.min(startPoint.value.y, current.y)
    const w = Math.abs(current.x - startPoint.value.x)
    const h = Math.abs(current.y - startPoint.value.y)

    // Ignore trop petits tracés (misclick)
    if (w > 0.01 && h > 0.005) {
      onDrawn({ x, y, width: w, height: h, confidence: 1, text: '', isDrawn: true })
    }

    isDrawing.value = false
    startPoint.value = null
    previewRect.value = null
  }

  function cancel () {
    isDrawing.value = false
    startPoint.value = null
    previewRect.value = null
  }

  return { isDrawing, previewRect, onMouseDown, onMouseMove, onMouseUp, cancel }
}

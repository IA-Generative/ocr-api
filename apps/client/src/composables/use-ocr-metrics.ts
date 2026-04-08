import type { components } from '@/api/types/api.schema'
import type { BboxReview } from '@/interfaces/review'
import type { DrawnBox } from '@/composables/use-box-drawing'

type Bbox = components['schemas']['Bbox']
type Page = components['schemas']['Page']

export interface PageMetrics {
  pageIdx: number
  totalBoxes: number
  avgConfidence: number
  reviewedCount: number
  validCount: number
  invalidCount: number
  correctedCount: number
}

export interface IoUResult {
  drawnBoxIdx: number
  nearestOcrBoxIdx: number | null
  nearestOcrText: string
  iou: number
}

export interface DocumentMetrics {
  totalPages: number
  totalBoxes: number
  avgConfidence: number
  minConfidence: number
  maxConfidence: number
  reviewedCount: number
  validCount: number
  invalidCount: number
  correctedCount: number
  lowConfidenceCount: number   // < 0.70
  mediumConfidenceCount: number // 0.70–0.90
  highConfidenceCount: number  // >= 0.90
  precision: number  // valid / (valid + invalid)
  reviewCoverage: number // reviewed / total
  pages: PageMetrics[]
}

function computeIoU (a: Bbox, b: Bbox): number {
  const ax2 = a.x + a.width
  const ay2 = a.y + a.height
  const bx2 = b.x + b.width
  const by2 = b.y + b.height

  const ix1 = Math.max(a.x, b.x)
  const iy1 = Math.max(a.y, b.y)
  const ix2 = Math.min(ax2, bx2)
  const iy2 = Math.min(ay2, by2)

  if (ix2 <= ix1 || iy2 <= iy1) return 0

  const intersection = (ix2 - ix1) * (iy2 - iy1)
  const union = a.width * a.height + b.width * b.height - intersection
  return union <= 0 ? 0 : intersection / union
}

export function computeDocumentMetrics (
  pages: Page[],
  corrections: Map<string, BboxReview>,
): DocumentMetrics {
  let totalBoxes = 0
  let sumConfidence = 0
  let minConf = 1
  let maxConf = 0
  let lowConf = 0
  let medConf = 0
  let highConf = 0
  let validCount = 0
  let invalidCount = 0
  let correctedCount = 0

  const pageMetrics: PageMetrics[] = pages.map((page, pageIdx) => {
    const boxes = page.boxes ?? []
    totalBoxes += boxes.length
    let pageSum = 0
    let pageValid = 0
    let pageInvalid = 0
    let pageCorrected = 0

    for (let boxIdx = 0; boxIdx < boxes.length; boxIdx++) {
      const box = boxes[boxIdx]
      sumConfidence += box.confidence
      pageSum += box.confidence
      if (box.confidence < minConf) minConf = box.confidence
      if (box.confidence > maxConf) maxConf = box.confidence
      if (box.confidence < 0.7) lowConf++
      else if (box.confidence < 0.9) medConf++
      else highConf++

      const review = corrections.get(`${pageIdx}-${boxIdx}`)
      if (review) {
        if (review.validation === 'valid') { validCount++; pageValid++ }
        else if (review.validation === 'invalid') { invalidCount++; pageInvalid++ }
        else { correctedCount++; pageCorrected++ }
      }
    }

    return {
      pageIdx,
      totalBoxes: boxes.length,
      avgConfidence: boxes.length ? pageSum / boxes.length : 0,
      reviewedCount: pageValid + pageInvalid + pageCorrected,
      validCount: pageValid,
      invalidCount: pageInvalid,
      correctedCount: pageCorrected,
    }
  })

  const reviewedTotal = validCount + invalidCount + correctedCount
  const precision = (validCount + invalidCount) > 0
    ? validCount / (validCount + invalidCount)
    : 0

  return {
    totalPages: pages.length,
    totalBoxes,
    avgConfidence: totalBoxes ? sumConfidence / totalBoxes : 0,
    minConfidence: totalBoxes ? minConf : 0,
    maxConfidence: totalBoxes ? maxConf : 0,
    reviewedCount: reviewedTotal,
    validCount,
    invalidCount,
    correctedCount,
    lowConfidenceCount: lowConf,
    mediumConfidenceCount: medConf,
    highConfidenceCount: highConf,
    precision,
    reviewCoverage: totalBoxes ? reviewedTotal / totalBoxes : 0,
    pages: pageMetrics,
  }
}

export function computePageIoU (
  ocrBoxes: Bbox[],
  drawnBoxes: DrawnBox[],
): IoUResult[] {
  return drawnBoxes.map((drawn, drawnIdx) => {
    let bestIoU = 0
    let bestOcrIdx: number | null = null

    for (let i = 0; i < ocrBoxes.length; i++) {
      const iou = computeIoU(drawn, ocrBoxes[i])
      if (iou > bestIoU) {
        bestIoU = iou
        bestOcrIdx = i
      }
    }

    return {
      drawnBoxIdx: drawnIdx,
      nearestOcrBoxIdx: bestOcrIdx,
      nearestOcrText: bestOcrIdx !== null ? (ocrBoxes[bestOcrIdx].text ?? '') : '',
      iou: bestIoU,
    }
  })
}

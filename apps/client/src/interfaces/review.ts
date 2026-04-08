export type ValidationState = 'valid' | 'invalid' | null

export interface BboxReview {
  correctedText: string
  validation: ValidationState
  isPrivate: boolean
}

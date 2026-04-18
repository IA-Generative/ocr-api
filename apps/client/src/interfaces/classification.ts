export interface PageLabel {
  /** Identifiant machine : [a-z0-9_-] uniquement, sans accent ni caractère spécial */
  key: string
  /** Description lisible par un humain, obligatoire pour les labels libres */
  definition: string
  /** true = label issu de la liste prédéfinie */
  predefined: boolean
  /** true = label issu d'une prédiction automatique, non supprimable manuellement */
  readonly?: boolean
  /** Score de confiance de la prédiction (0-1), uniquement pour les labels readonly */
  confidence?: number
  /** Modèle ayant produit la prédiction */
  model?: { name: string; version: string; device?: string }
  /** Avis utilisateur sur la prédiction : valid, invalid ou null (non évalué) */
  validation?: 'valid' | 'invalid' | null
}

export type PageClassifications = Map<number, PageLabel[]>

/** Transforme une chaîne en slug valide ([a-z0-9_-]) */
export function toSlug (value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // supprime les diacritiques
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
}

/** Vérifie qu'un slug est valide */
export function isValidSlug (value: string): boolean {
  return /^[a-z0-9][a-z0-9_-]*$/.test(value)
}

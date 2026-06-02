// Types de fichiers acceptés à l'upload (OCR / extractions)

// Types MIME validés côté client avant envoi.
// Certains navigateurs renvoient un type MIME vide ou non standard pour les
// fichiers bureautiques : on complète donc la validation par l'extension.
export const VALID_MIME_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  // CSV
  'text/csv',
  'application/csv',
  // DOCX / DOC
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'application/docx',
  // XLSX / XLS
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/xlsx',
  // OpenDocument
  'application/vnd.oasis.opendocument.text',
  'application/vnd.oasis.opendocument.spreadsheet',
  'application/vnd.oasis.opendocument.presentation',
  // Email
  'message/rfc822',
]

// Extensions acceptées (utilisées pour l'attribut `accept` et le fallback de validation).
export const VALID_EXTENSIONS = [
  '.pdf',
  '.jpg',
  '.jpeg',
  '.png',
  '.csv',
  '.docx',
  '.xlsx',
  '.odt',
  '.ods',
  '.odp',
  '.eml',
]

// Valeur de l'attribut HTML `accept` pour les inputs de type file.
export const UPLOAD_ACCEPT = VALID_EXTENSIONS.join(',')

// Texte d'aide affiché à l'utilisateur.
export const UPLOAD_FORMATS_LABEL = 'PDF, JPG, PNG, CSV, DOCX, XLSX, ODT, ODS, ODP, EML'

/**
 * Indique si un fichier possède une extension acceptée.
 */
export function hasValidExtension (fileName: string): boolean {
  const lower = fileName.toLowerCase()
  return VALID_EXTENSIONS.some(ext => lower.endsWith(ext))
}

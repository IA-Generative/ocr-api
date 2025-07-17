
export interface BoxItem {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  text: string
}

export interface PageItem {
  page: number
  page_url: string
  boxes: BoxItem[]
}

export interface OutputData {
  type: string
  model_name: string
  created_at: number
  updated_at: number
  version: string
  total_pages: number
  pages: PageItem[]
  extras: unknown
}

export interface IOcr {
  id: string
  user_id: string
  type: string
  status: string
  percentage: number
  position: number
  input: {
    storage_file_path: string
    raw_filename: string
    content_type: string
    ext: string
    size: number
  }
  output: OutputData | null
  created_at: number
  updated_at: number
  extras: Record<string, unknown>
  error: string | null
}

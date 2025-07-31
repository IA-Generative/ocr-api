export function openLink (url: string) {
  window.open(url, '_blank')
}

export function countWords (text: string) {
  return text.replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, '').split(' ').filter(word => word.length > 0).length
}

export function getCurrentDate () {
  const date = new Date()
  return date.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function formattedDate (date: Date) {
  const dateFormat = new Date(date)
  return dateFormat.toLocaleDateString()
}

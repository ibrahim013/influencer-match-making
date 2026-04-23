export function creatorAvatarUrl(handle: string): string {
  const seed = encodeURIComponent(handle.replace(/^@/, '') || 'creator')
  return `https://api.dicebear.com/7.x/lorelei/svg?seed=${seed}`
}

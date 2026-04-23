/**
 * Backend metadata does not yet include platforms; infer chips for layout only.
 * TODO: replace with platforms[] from API when available.
 */
export function inferPlatforms(niche: string): string[] {
  const n = niche.toLowerCase()
  const out: string[] = []
  if (
    n.includes('linkedin') ||
    n.includes('b2b') ||
    n.includes('professional') ||
    n.includes('career')
  ) {
    out.push('LinkedIn')
  }
  if (
    n.includes('tiktok') ||
    n.includes('short') ||
    n.includes('viral') ||
    n.includes('dance')
  ) {
    out.push('TikTok')
  }
  if (
    n.includes('instagram') ||
    n.includes('lifestyle') ||
    n.includes('wellness') ||
    n.includes('fashion') ||
    n.includes('food') ||
    n.includes('running') ||
    n.includes('eco') ||
    n.includes('sustainability') ||
    out.length === 0
  ) {
    out.push('Instagram')
  }
  return [...new Set(out)].slice(0, 2)
}

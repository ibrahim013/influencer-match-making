import { creatorAvatarUrl } from '@/lib/avatar-url'
import { cn } from '@/lib/utils'

export function CreatorAvatar({
  handle,
  className,
  size = 48,
}: {
  handle: string
  className?: string
  size?: number
}) {
  return (
    <img
      src={creatorAvatarUrl(handle)}
      alt=""
      width={size}
      height={size}
      className={cn('rounded-full border border-border bg-muted object-cover', className)}
      loading="lazy"
    />
  )
}

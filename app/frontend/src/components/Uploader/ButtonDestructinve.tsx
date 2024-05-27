import { Button } from "@/components/ui/button"

export function ButtonDestructive({title, onClick}:{
    title: string
    onClick?: () => void
}) {
    return <Button onClick={onClick} variant="destructive">{title}</Button>
}

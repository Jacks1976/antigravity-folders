import BibleReader from '@/components/BibleReader'

export const metadata = {
    title: 'Bíblia - MyChurchPad',
}

export default function BiblePage() {
    return (
        <div className="max-w-4xl mx-auto p-6">
            <BibleReader />
        </div>
    )
}

export default function BibleReader() {
    const bibleVerses = [
        { ref: 'João 3:16', text: 'Porque Deus amou o mundo de tal maneira que deu seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.' },
        { ref: 'Salmos 23:1', text: 'O Senhor é o meu pastor, nada me faltará.' },
        { ref: 'Romanos 12:2', text: 'E não vos conformeis com este mundo, mas transformai-vos pela renovação do vosso entendimento, para que experimenteis qual seja a boa, agradável, e perfeita vontade de Deus.' },
    ];

    const randomVerse = bibleVerses[Math.floor(Math.random() * bibleVerses.length)];

    return (
        <div className="p-8 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg shadow-lg border-l-4 border-blue-600">
            <h2 className="text-2xl font-bold mb-4 text-blue-900">📖 Bíblia Online</h2>
            
            <div className="bg-white p-6 rounded-lg mb-4 border border-blue-200">
                <p className="text-sm text-gray-600 mb-2 font-semibold">{randomVerse.ref}</p>
                <p className="text-lg text-gray-800 italic">{randomVerse.text}</p>
            </div>
            
            <a 
                href="https://www.bible.com/pt" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
                Abrir Bíblia Online →
            </a>
            <p className="text-xs text-gray-600 mt-3">Powered by Bible.com</p>
        </div>
    );
}

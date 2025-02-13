import './globals.css'

export const metadata = {
  title: 'RAG Document Analyzer',
  description: 'Interface de configuration et d\'analyse de documents avec RAG',
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}

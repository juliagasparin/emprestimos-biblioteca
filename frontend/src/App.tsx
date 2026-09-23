import { useState } from 'react'
import './App.css'

// 1. Tipagem exata baseada no contrato do backend
interface DisponibilidadeResultado {
  livro_id: number
  total: number
  disponiveis: number
  em_estoque: boolean
}

function App() {
  // Estados para input e controle da busca
  const [livroIdInput, setLivroIdInput] = useState<string>('1')
  const [resultado, setResultado] = useState<DisponibilidadeResultado | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [erro, setErro] = useState<string | null>(null)

  // Função para buscar a disponibilidade na API FastAPI
  const buscarDisponibilidade = async () => {
    if (!livroIdInput.trim()) return

    setLoading(true)
    setErro(null)
    setResultado(null)

    try {
      const response = await fetch(`http://localhost:8000/disponibilidade/${livroIdInput}`)
      
      if (response.status === 404) {
        throw new Error('Livro não encontrado ou sem exemplares cadastrados.')
      }

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.statusText}`)
      }

      const data: DisponibilidadeResultado = await response.json()
      setResultado(data)
    } catch (err: any) {
      setErro(err.message || 'Erro ao conectar com o servidor.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '500px', margin: '40px auto', fontFamily: 'sans-serif', textAlign: 'left' }}>
      <h2>Consulta de Disponibilidade de Livro</h2>

      {/* 3.1 Input + Botão */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        <input
          type="number"
          value={livroIdInput}
          onChange={(e) => setLivroIdInput(e.target.value)}
          placeholder="Digite o ID do livro"
          style={{ padding: '8px', fontSize: '16px', width: '100%' }}
        />
        <button 
          onClick={buscarDisponibilidade}
          disabled={loading}
          style={{ padding: '8px 16px', fontSize: '16px', cursor: 'pointer' }}
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </div>

      {/* 3.4 Renderização Condicional */}
      {loading && <p>Carregando dados do livro...</p>}

      {erro && (
        <div style={{ color: 'red', padding: '10px', border: '1px solid red', borderRadius: '4px' }}>
          <strong>Erro:</strong> {erro}
        </div>
      )}

      {resultado && (
        <div style={{ padding: '15px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9', color: '#333' }}>
          <h3>Status do Livro #{resultado.livro_id}</h3>
          <p><strong>Total de exemplares:</strong> {resultado.total}</p>
          <p><strong>Disponíveis para empréstimo:</strong> {resultado.disponiveis}</p>
          <p><strong>Em estoque:</strong> {resultado.em_estoque ? 'Sim ✅' : 'Não ❌'}</p>
        </div>
      )}
    </div>
  )
}

export default App
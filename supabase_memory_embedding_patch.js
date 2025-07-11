
/* 
🔧 PATCH pour ajouter embeddings à l'API mémoire
À intégrer dans supabase/functions/jarvys-dashboard/index.ts
*/


// Fonction pour calculer les embeddings OpenAI
async function calculateEmbedding(text: string): Promise<number[]> {
  try {
    const openaiKey = Deno.env.get('OPENAI_API_KEY');
    if (!openaiKey) {
      console.warn('⚠️ OPENAI_API_KEY manquant pour embeddings');
      return [];
    }

    const response = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'text-embedding-ada-002',
        input: text,
      }),
    });

    if (!response.ok) {
      console.error('❌ Erreur API OpenAI embeddings:', response.status);
      return [];
    }

    const data = await response.json();
    return data.data[0].embedding;
  } catch (error) {
    console.error('❌ Erreur calcul embedding:', error);
    return [];
  }
}


/* 
Modifier l'endpoint /api/memory pour inclure:

if (url.pathname === '/api/memory' && request.method === 'POST') {
  const body = await request.json();
  const { content, type = 'user_interaction' } = body;
  
  // Calculer l'embedding
  const embedding = await calculateEmbedding(content);
  
  // Insérer avec embedding
  const memoryData = {
    content,
    type,
    embedding: embedding.length > 0 ? embedding : null,
    timestamp: new Date().toISOString(),
    agent_id: 'jarvys_dev_cloud'
  };
  
  const { error } = await supabase
    .from('jarvys_memory')
    .insert(memoryData);
    
  if (error) {
    return new Response(JSON.stringify({ error: error.message }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  return new Response(JSON.stringify({ success: true, embedding_length: embedding.length }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
*/

import { describe, it, expect, vi, beforeEach } from "vitest";
import { Api } from "./API";

describe('API Client', () => {
    let api: Api;

    beforeEach(() => {
        vi.resetAllMocks();
        api = new Api('http://localhost/api/', 'accounts/refresh/', 'accounts/csrf/');
    });

    it('deve buscar o token CSRF e injetar no cabeçalho da requisição antes de fazer o POST', async () => {
        // Simula o fetch do CSRF e depois o post
        const fetchMock = vi.spyOn(global, 'fetch')
        .mockResolvedValueOnce(new Response(JSON.stringify({csrf_token: 'meu_token_secreto'}), {status: 200}))
        .mockResolvedValueOnce(new Response(JSON.stringify({ok: true}), {status: 200}));

        const response = await api.post('teste/', {body: JSON.stringify({nome: 'Sushi'})});

        expect(fetchMock).toHaveBeenCalledTimes(2);
        // Primeiro fetch busca o csrf
        expect(fetchMock.mock.calls[0][0]).toBe('http://localhost/api/accounts/csrf/');
        // Segundo fetch busca a rota com o token csrf no header X-CSRFToken
        const headersEnviados = fetchMock.mock.calls[1][1]?.headers as Headers;
        expect(headersEnviados.get('X-CSRFToken')).toBe('meu_token_secreto');
        expect(response.status).toBe(200);
    });

    it('deve chamar a rota de refresh se receber uma resposta 401', async () => {
        const fetchMock = vi.spyOn(global, 'fetch')
        .mockResolvedValueOnce(new Response(null, {status: 401})) // Primeira requisição recebe 401, sem autorização
        .mockResolvedValueOnce(new Response(JSON.stringify({csrf_token: 'fake-csrf-token'}), {status: 200})) // Busca o token csrf que protege a rota de refresh
        .mockResolvedValueOnce(new Response(JSON.stringify({message: 'ok'}), {status: 200})) // Refresh realizado com sucesso
        .mockResolvedValueOnce(new Response(JSON.stringify({dados: 'sucesso'}), {status: 200})); // Retry na rota com sucesso

        const response = await api.get('pedidos/');

        expect(fetchMock).toHaveBeenCalledTimes(4);
        expect(fetchMock.mock.calls[1][0]).toBe('http://localhost/api/accounts/csrf/');
        expect(fetchMock.mock.calls[2][0]).toBe('http://localhost/api/accounts/refresh/');
        expect(response.status).toBe(200)
    });

    it('não deve acessar a rota accounts/csrf/ se o parâmetro csrf for passado como false em rotas diferentes de get', async () => {
        const fetchMock = vi.spyOn(global, 'fetch')
        .mockResolvedValueOnce(new Response(JSON.stringify({ok: true}), {status: 200}));

        await api.post('login/', {}, false);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        const headers = fetchMock.mock.calls[0][1]?.headers as Headers | undefined;
        expect(headers?.get?.('X-CSRFToken')).toBeFalsy();
    });

});
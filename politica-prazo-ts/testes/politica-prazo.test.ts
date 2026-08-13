import { describe, it, expect } from 'vitest';
import { PrazoPadrao } from '../src/dominio/politica-prazo';

describe('PrazoPadrao', () => {
  it('retorna 14 dias por padrão', () => {
    const politica = new PrazoPadrao();
    expect(politica.calcularDias(1, 1)).toBe(14);
  });

  it('retorna o valor customizado passado no construtor', () => {
    const politica = new PrazoPadrao(7);
    expect(politica.calcularDias(1, 1)).toBe(7);
  });
});
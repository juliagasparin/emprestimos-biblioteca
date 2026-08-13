// src/dominio/politica-prazo.ts

export interface PoliticaPrazo {
  calcularDias(usuarioId: number, livroId: number): number;
}

export class PrazoPadrao implements PoliticaPrazo {
  constructor(private readonly prazoDias: number = 14) {}

  calcularDias(usuarioId: number, livroId: number): number {
    return this.prazoDias;
  }
}
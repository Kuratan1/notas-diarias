import React from "react";
import { AbsoluteFill } from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";
import { z } from "zod";

// Frase no estilo "bloco de notas do celular" (feed 4:5). Claro ou escuro.
// Sem logo nem marca de terceiros: só a linguagem visual do app.

const { fontFamily } = loadFont("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });

export const NOTAS = { width: 1080, height: 1350 };

export const notasSchema = z.object({
  titulo: z.string(),
  frase: z.string(),
  data: z.string(),
  hora: z.string(),
  escuro: z.boolean(),
  arroba: z.string(),
});

export const NOTAS_EXEMPLOS: z.infer<typeof notasSchema>[] = [
  {
    titulo: "bom dia",
    frase: "Café quente, céu limpo e nenhuma pressa.\n\nÀs vezes é só isso.",
    data: "17 de novembro de 2026 às 06:48",
    hora: "6:48",
    escuro: false,
    arroba: "@eduardovieira",
  },
  {
    titulo: "lembrete pra mim",
    frase: "Tem alegria que cabe numa xícara.\n\nComeça o dia por ela.",
    data: "18 de novembro de 2026 às 07:05",
    hora: "7:05",
    escuro: false,
    arroba: "@eduardovieira",
  },
  {
    titulo: "anote agora",
    frase: "Coisas boas também acontecem sem aviso.\n\nFica atento hoje.",
    data: "19 de novembro de 2026 às 06:31",
    hora: "6:31",
    escuro: true,
    arroba: "@eduardovieira",
  },
];

const AMARELO = "#E3A008";

const Chevron: React.FC<{ cor: string }> = ({ cor }) => (
  <svg width="30" height="52" viewBox="0 0 15 26">
    <path d="M13 2 L2.5 13 L13 24" fill="none" stroke={cor} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Compartilhar: React.FC<{ cor: string }> = ({ cor }) => (
  <svg width="46" height="58" viewBox="0 0 23 29" fill="none" stroke={cor} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11.5 2 V18" />
    <path d="M6 7 L11.5 1.8 L17 7" />
    <path d="M7 11 H3.5 V27 H19.5 V11 H16" />
  </svg>
);

const Mais: React.FC<{ cor: string }> = ({ cor }) => (
  <svg width="58" height="58" viewBox="0 0 29 29">
    <circle cx="14.5" cy="14.5" r="12.5" fill="none" stroke={cor} strokeWidth="2.2" />
    {[8.5, 14.5, 20.5].map((x) => (
      <circle key={x} cx={x} cy="14.5" r="1.9" fill={cor} />
    ))}
  </svg>
);

const BarraStatus: React.FC<{ hora: string; cor: string }> = ({ hora, cor }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: 70 }}>
    <span style={{ fontSize: 38, fontWeight: 600, color: cor, letterSpacing: "-0.01em" }}>{hora}</span>
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
      <svg width="44" height="28" viewBox="0 0 22 14">
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={i * 5.8} y={10 - i * 3.2} width="4" height={4 + i * 3.2} rx="1" fill={cor} />
        ))}
      </svg>
      <svg width="40" height="28" viewBox="0 0 20 14" fill="none" stroke={cor} strokeWidth="2.2" strokeLinecap="round">
        <path d="M1.5 5 A12 12 0 0 1 18.5 5" />
        <path d="M5 8.5 A7 7 0 0 1 15 8.5" />
        <circle cx="10" cy="12" r="1.2" fill={cor} stroke="none" />
      </svg>
      <svg width="60" height="28" viewBox="0 0 30 14">
        <rect x="0.8" y="0.8" width="25" height="12.4" rx="3.5" fill="none" stroke={cor} strokeOpacity="0.45" strokeWidth="1.4" />
        <rect x="2.8" y="2.8" width="17" height="8.4" rx="2" fill={cor} />
        <rect x="27.3" y="4.6" width="1.8" height="4.8" rx="0.9" fill={cor} fillOpacity="0.45" />
      </svg>
    </div>
  </div>
);

export const FraseNotas: React.FC<z.infer<typeof notasSchema>> = ({ titulo, frase, data, hora, escuro, arroba }) => {
  const fundo = escuro ? "#000000" : "#FFFFFF";
  const tinta = escuro ? "#FFFFFF" : "#000000";
  const cinza = escuro ? "#8E8E93" : "#8A8A8E";
  return (
    <AbsoluteFill style={{ backgroundColor: fundo, fontFamily, color: tinta, padding: "36px 64px 0" }}>
      <BarraStatus hora={hora} cor={tinta} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 34 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Chevron cor={AMARELO} />
          <span style={{ fontSize: 44, color: AMARELO, letterSpacing: "-0.01em" }}>Notas</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 44 }}>
          <Compartilhar cor={AMARELO} />
          <Mais cor={AMARELO} />
        </div>
      </div>
      <div style={{ textAlign: "center", fontSize: 30, color: cinza, marginTop: 58 }}>{data}</div>
      <div style={{ marginTop: 52, display: "flex", flexDirection: "column", gap: 40 }}>
        <div style={{ fontSize: 66, fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1.15 }}>{titulo}</div>
        {frase.split("\n\n").map((p, i) => (
          <p key={i} style={{ margin: 0, fontSize: 54, lineHeight: 1.38, letterSpacing: "-0.012em" }}>
            {p}
          </p>
        ))}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 70, textAlign: "center", fontSize: 28, color: cinza, letterSpacing: "0.02em" }}>
        {arroba}
      </div>
    </AbsoluteFill>
  );
};

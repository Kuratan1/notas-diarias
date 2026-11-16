import React from "react";
import { Composition } from "remotion";
import { FraseNotas, NOTAS, notasSchema, NOTAS_EXEMPLOS } from "./FraseNotas";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Nota"
    component={FraseNotas}
    schema={notasSchema}
    durationInFrames={1}
    fps={30}
    {...NOTAS}
    defaultProps={NOTAS_EXEMPLOS[0]}
  />
);

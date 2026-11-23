import VersionProject from "@/components/atoms/Version";

export default function Home(){
  return(
    <div>
      <h1>Projeto do Sushiman Configurado</h1>

      <h2>
        Aqui será o catálogo de produtos do sushiman
      </h2>

      {<VersionProject/>}
    </div>
  );
}

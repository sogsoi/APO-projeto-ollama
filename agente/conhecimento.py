"""Conhecimento verificado, dividido por tópico, e a pedagogia própria de cada padrão.

Nada aqui chama o modelo. O tutor consulta `Padrao.fatos(...)` e injeta só os
tópicos que a pergunta pede, o que reduz alucinação e deixa as respostas focadas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# intenção -> tópicos de fatos que o modelo recebe
CONTEXTO_GERAL = (
    "Um padrão de projeto é uma solução reutilizável, nomeada e documentada, para um "
    "problema que se repete no projeto de software orientado a objetos. Não é código "
    "pronto nem biblioteca: é um modelo de organização de classes e responsabilidades "
    "que se adapta ao contexto. Dar nome ao padrão cria um vocabulário comum entre "
    "desenvolvedores. O catálogo GoF vem do livro 'Design Patterns: Elements of "
    "Reusable Object-Oriented Software' (1994), de Gamma, Helm, Johnson e Vlissides, "
    "conhecidos como 'Gang of Four', e descreve 23 padrões. Eles se dividem em três "
    "categorias: criacionais (como objetos são criados), estruturais (como classes e "
    "objetos se combinam em estruturas maiores) e comportamentais (como objetos se "
    "comunicam e dividem responsabilidades). Cada padrão é descrito por nome, problema, "
    "solução e consequências."
)

# intenção -> tópicos de fatos que o modelo recebe
TOPICOS_POR_INTENCAO: dict[str, tuple[str, ...]] = {
    "contexto": ("contexto", "definicao"),
    "conceito": ("definicao", "analogia"),
    "problema": ("problema",),
    "participantes": ("participantes", "mecanismo", "uml"),
    "mecanismo": ("mecanismo", "participantes"),
    "custos": ("custos",),
    "quando": ("usar", "evitar"),
    "confusoes": ("confusoes",),
    "erro": ("erro", "mecanismo"),
    "fechamento": ("custos", "evitar", "erro", "confusoes"),
    "duvida": ("definicao", "problema", "participantes", "mecanismo", "custos",
               "usar", "evitar", "confusoes", "erro"),
}

DESCRICAO_INTENCAO = {
    "contexto": "o que é um padrão de projeto, o catálogo GoF e a categoria do padrão",
    "conceito": "o que é o padrão (definição e intenção)",
    "problema": "que problema o padrão resolve",
    "participantes": "quem são os participantes e como colaboram",
    "mecanismo": "por que o padrão funciona (interface, composição, polimorfismo)",
    "custos": "o que o padrão custa e o que ele entrega",
    "quando": "quando usar e quando evitar",
    "confusoes": "com qual padrão ele costuma ser confundido",
    "erro": "o erro mais comum ao aplicá-lo",
    "exemplo": "um exemplo em Java",
    "fechamento": "o que lembrar antes de usar o padrão",
    "comparar": "como distinguir Strategy e Adapter",
}


@dataclass(frozen=True)
class Padrao:
    nome: str
    categoria: str
    definicao: str
    intencao_padrao: str
    problema: str
    participantes: tuple[str, ...]
    mecanismo: str
    consequencias: tuple[str, ...]
    quando_usar: tuple[str, ...]
    quando_evitar: tuple[str, ...]
    confusoes: dict[str, str]
    sinal_pratico: str
    erro_comum: str
    analogia: str
    # pedagogia própria
    gancho: str
    estrategia: str
    progressao: tuple[str, ...]
    perguntas: dict[str, str]
    # exemplo verificado
    exemplo_java: str
    uml: str
    o_que_observar: str
    se_amanha: str
    # exercício
    dominio_exercicio: str
    exercicio_fixo: str
    termos_proibidos_exercicio: tuple[str, ...]
    termos_invalidos: tuple[str, ...]
    palavras_chave: tuple[str, ...]
    contexto_categoria: str
    confusao_principal: str = ""

    def fatos(self, topicos: tuple[str, ...] | list[str]) -> str:
        blocos = {
            "contexto": lambda: f"CONTEXTO GERAL: {CONTEXTO_GERAL}\nCATEGORIA: {self.contexto_categoria}",
            "definicao": lambda: f"DEFINIÇÃO: {self.definicao}\nINTENÇÃO: {self.intencao_padrao}",
            "problema": lambda: f"PROBLEMA QUE RESOLVE: {self.problema}",
            "analogia": lambda: f"ANALOGIA (ilustrativa, não faz parte do catálogo GoF): {self.analogia}",
            "participantes": lambda: "PARTICIPANTES: " + "; ".join(self.participantes),
            "mecanismo": lambda: f"MECANISMO: {self.mecanismo}",
            "custos": lambda: "CONSEQUÊNCIAS: " + "; ".join(self.consequencias),
            "usar": lambda: "QUANDO USAR: " + "; ".join(self.quando_usar),
            "evitar": lambda: "QUANDO EVITAR: " + "; ".join(self.quando_evitar),
            "confusoes": lambda: (
                "CONFUSÕES FREQUENTES: "
                + "; ".join(f"{self.nome} × {k}: {v}" for k, v in self.confusoes.items())
                + f"\nSINAL PRÁTICO: {self.sinal_pratico}"
            ),
            "erro": lambda: f"ERRO COMUM: {self.erro_comum}",
            "uml": lambda: f"ESTRUTURA (UML simplificado):\n{self.uml}",
        }
        return f"PADRÃO: {self.nome} ({self.categoria})\n" + "\n".join(
            blocos[t]() for t in topicos if t in blocos
        )

    def pergunta_final(self, intencao: str) -> str:
        return self.perguntas.get(intencao, self.perguntas["padrao"])

    def vizinhos(self) -> tuple[str, ...]:
        return tuple(self.confusoes)


STRATEGY = Padrao(
    nome="Strategy",
    categoria="padrão comportamental (GoF)",
    definicao=(
        "Define uma família de algoritmos, encapsula cada um deles e os torna "
        "intercambiáveis, permitindo que o algoritmo varie independentemente dos "
        "clientes que o utilizam."
    ),
    intencao_padrao=(
        "Isolar a variação de comportamento atrás de uma interface comum, para que o "
        "Context delegue a execução a um objeto Strategy em vez de decidir com "
        "condicionais. O Context não sabe qual algoritmo está usando; o cliente "
        "escolhe e injeta a estratégia."
    ),
    problema=(
        "Um aplicativo de navegação começa calculando rotas apenas por rodovias. Depois "
        "ganha caminhada, bicicleta e transporte público. Se cada variante entra como "
        "mais um if/else dentro do mesmo método, o código cresce a cada novo meio de "
        "transporte, mistura a regra de cálculo com a escolha do algoritmo e fica "
        "difícil de testar. O mesmo acontece com cálculo de frete, desconto ou "
        "ordenação: várias formas de executar a mesma tarefa, escondidas atrás de "
        "condicionais."
    ),
    participantes=(
        "Context: mantém uma referência a Strategy e delega a ele a execução",
        "Strategy: interface comum dos algoritmos",
        "ConcreteStrategy: implementações concretas (uma por variante)",
        "Cliente: escolhe e injeta a ConcreteStrategy no Context",
    ),
    mecanismo=(
        "O Context guarda uma referência do tipo da interface Strategy (composição) e, "
        "quando precisa executar a tarefa, apenas chama o método da interface. O "
        "polimorfismo decide qual código roda. A escolha do algoritmo sai do Context e "
        "passa para o cliente, que injeta a estratégia pelo construtor ou por um setter, "
        "inclusive em tempo de execução. Acrescentar uma variante é criar uma nova "
        "ConcreteStrategy; o Context não muda (princípio Aberto/Fechado)."
    ),
    consequencias=(
        "Famílias de algoritmos reutilizáveis e testáveis isoladamente",
        "Elimina condicionais de seleção no Context",
        "Permite trocar o algoritmo em tempo de execução",
        "O Context não precisa conhecer os detalhes de cada algoritmo",
        "Custo: o cliente precisa conhecer as estratégias disponíveis",
        "Custo: aumenta o número de objetos e há comunicação Context/Strategy",
    ),
    quando_usar=(
        "Muitas classes relacionadas diferem apenas no comportamento",
        "São necessárias variantes de um algoritmo",
        "O algoritmo precisa ser escolhido em tempo de execução",
        "O algoritmo usa dados que o cliente não deve conhecer",
        "Regras de negócio mudam com frequência e precisam ser testadas à parte",
        "Uma classe define muitos comportamentos que aparecem como condicionais",
    ),
    quando_evitar=(
        "Existem poucas variantes e elas não mudam",
        "O comportamento é fixo e simples: uma condicional resolve com menos código",
        "O cliente não tem como decidir qual estratégia usar",
        "As variantes compartilham quase todo o código e diferem em um detalhe "
        "(Template Method pode ser mais adequado)",
        "A escolha depende do estado interno do objeto e muda sozinha (State modela "
        "melhor as transições)",
    ),
    confusoes={
        "State": (
            "em State, o objeto muda de comportamento quando seu estado interno muda e as "
            "transições são responsabilidade dos estados; em Strategy, a escolha é "
            "externa e os algoritmos são independentes entre si"
        ),
        "Template Method": (
            "Strategy usa composição e troca o algoritmo inteiro em tempo de execução; "
            "Template Method usa herança e fixa o esqueleto do algoritmo, variando "
            "apenas passos"
        ),
        "Adapter": (
            "Adapter converte uma interface incompatível; Strategy seleciona entre "
            "algoritmos que já têm a mesma interface"
        ),
    },
    sinal_pratico=(
        "Pergunte quem inicia a troca de comportamento. Se a escolha vem de fora e pode "
        "ser trocada em tempo de execução (o cliente injeta outra estratégia), é "
        "Strategy. Se o próprio objeto muda de comportamento quando seu estado interno "
        "muda e as transições pertencem aos estados, é State."
    ),
    erro_comum=(
        "Criar a interface Strategy, mas manter o if/else dentro do Context para "
        "escolher a implementação. O condicional só mudou de lugar e o padrão perdeu o "
        "propósito: a escolha deve vir de fora, injetada no Context."
    ),
    analogia=(
        "uma furadeira com brocas intercambiáveis: o corpo da furadeira (Context) é o "
        "mesmo e quem usa encaixa a broca que quiser (ConcreteStrategy)."
    ),
    gancho=(
        "Comece por um método de cálculo com if/else por tipo (pseudocódigo de 3 a 4 "
        "linhas) e pergunte ao aluno o que acontece quando chegar a quinta variante."
    ),
    estrategia=(
        "Refatoração guiada: parta do código ruim, deixe o aluno sentir a dor e só então "
        "apresente a solução. Sempre diga o que varia e o que permanece estável."
    ),
    progressao=("contexto", "conceito", "problema", "mecanismo", "participantes",
                "exemplo", "custos", "quando", "confusoes", "erro"),
    perguntas={
        "padrao": "Quer ver como isso fica em código ou prefere testar com um exercício?",
        "contexto": "Faz sentido até aqui? Posso detalhar a ideia do Strategy ou, se preferir, mostrar o problema que ele resolve.",
        "conceito": "Quer que eu mostre o problema que ele resolve, para ficar mais concreto?",
        "problema": "Você já viu um código assim, com if/else crescendo? O que, no seu if/else, varia e o que permanece igual?",
        "mecanismo": "Se aparecer uma nova variante, qual classe você precisaria editar?",
        "participantes": "Em um sistema de frete, quem faria o papel de Context?",
        "custos": "Em que situação trocar um if/else por esse padrão seria exagero?",
        "quando": "Pense num caso seu: com quantas variantes você já justificaria usar o padrão?",
        "confusoes": "Num objeto que muda de comportamento sozinho, quem decide a troca?",
        "erro": "Onde, no código, você procuraria o sinal desse erro?",
        "exemplo": "Que outra variante você acrescentaria, e o que NÃO precisaria mudar?",
        "fechamento": "Quer praticar com um exercício para fixar esses pontos?",
    },
    exemplo_java="""\
// interface comum das rotas
interface RotaStrategy {
    Rota calcular(String origem, String destino);
}

// resultado do cálculo
class Rota {
    private final String descricao;
    private final double distanciaKm;
    Rota(String descricao, double distanciaKm) {
        this.descricao = descricao;
        this.distanciaKm = distanciaKm;
    }
    @Override public String toString() {
        return descricao + " (" + distanciaKm + " km)";
    }
}

// uma implementação por meio de transporte; distâncias só para exemplo
class RotaCarro implements RotaStrategy {
    public Rota calcular(String origem, String destino) {
        return new Rota("Rodovia de " + origem + " a " + destino, 12.0);
    }
}

class RotaCaminhada implements RotaStrategy {
    public Rota calcular(String origem, String destino) {
        return new Rota("Caminhada de " + origem + " a " + destino, 4.5);
    }
}

class RotaBicicleta implements RotaStrategy {
    public Rota calcular(String origem, String destino) {
        return new Rota("Ciclovia de " + origem + " a " + destino, 6.0);
    }
}

// Context: delega o cálculo e permite trocar a estratégia
class Navegador {
    private RotaStrategy estrategia;
    Navegador(RotaStrategy estrategia) { this.estrategia = estrategia; }
    void setEstrategia(RotaStrategy estrategia) { this.estrategia = estrategia; }
    Rota calcularRota(String origem, String destino) {
        return estrategia.calcular(origem, destino);
    }
}

public class Main {
    public static void main(String[] args) {
        Navegador navegador = new Navegador(new RotaCarro());
        System.out.println(navegador.calcularRota("Casa", "Trabalho"));
        navegador.setEstrategia(new RotaBicicleta());
        System.out.println(navegador.calcularRota("Casa", "Trabalho"));
    }
}
""",
    uml=(
        "Cliente ──► Navegador (Context) ◇──► «interface» RotaStrategy\n"
        "                                          ▲\n"
        "                       ┌──────────────────┼──────────────────┐\n"
        "                  RotaCarro         RotaCaminhada       RotaBicicleta"
    ),
    o_que_observar=(
        "A interface comum é RotaStrategy. O Navegador guarda uma referência a ela "
        "(composição) e só chama estrategia.calcular, sem nenhum if/else. Quem escolhe "
        "a estratégia é o cliente, no main, com new Navegador(new RotaCarro()) e depois "
        "setEstrategia(new RotaBicicleta()): a mesma chamada calcularRota produz rotas "
        "diferentes em tempo de execução. As distâncias são ilustrativas."
    ),
    se_amanha=(
        "Se amanhã surgir o transporte por patinete, basta criar RotaPatinete "
        "implementando RotaStrategy. O Navegador, a interface e as outras rotas não "
        "mudam."
    ),
    dominio_exercicio="cálculo de desconto numa loja",
    exercicio_fixo=(
        "**Cenário:** Uma loja calcula o total do carrinho num único método com vários "
        "if/else: cliente comum, estudante, cliente VIP e campanha de fim de ano. A cada "
        "semana o marketing cria uma regra nova, e cada mudança obriga a editar e retestar "
        "o método inteiro.\n\n"
        "**Sua tarefa:** Descreva como reorganizar as classes para que uma nova regra de "
        "desconto não exija alterar o método que fecha a compra. Diga o que varia, o que "
        "fica estável e quem decide qual regra usar.\n\n"
        "**Critérios de sucesso:**\n"
        "- Você separou o que varia do que permanece estável.\n"
        "- O código que fecha a compra não escolhe a regra com condicionais.\n"
        "- Está claro quem escolhe a regra e como ela chega ao código que a usa.\n\n"
        "**Para começar:**\n"
        "1. Qual parte do método muda toda semana e qual nunca muda?\n"
        "2. Se a regra fosse uma peça que se encaixa, que contrato ela precisaria cumprir?\n\n"
        "Responda começando por **Minha resposta:**"
    ),
    termos_proibidos_exercicio=("Strategy", "Context", "Adapter", "Target", "Adaptee"),
    termos_invalidos=("Adaptee",),
    palavras_chave=("strategy", "estrategia"),
    contexto_categoria=("Strategy é comportamental: trata de como os objetos dividem "
                        "responsabilidades e executam comportamento."),
    confusao_principal="State",
)

ADAPTER = Padrao(
    nome="Adapter",
    categoria="padrão estrutural (GoF)",
    definicao=(
        "Converte a interface de uma classe em outra interface que o cliente espera. "
        "Permite que classes com interfaces incompatíveis trabalhem juntas."
    ),
    intencao_padrao=(
        "Reutilizar uma classe ou biblioteca existente cuja interface não corresponde à "
        "esperada pelo cliente, sem alterar o código original. O Adapter fica entre os "
        "dois: implementa o Target que o cliente já espera e traduz cada chamada para o "
        "formato que o Adaptee entende."
    ),
    problema=(
        "Um sistema de vendas precisa cobrar por duas bibliotecas de pagamento de "
        "terceiros. Uma recebe o valor em centavos e devolve um código numérico; a outra "
        "recebe o valor em reais e lança exceção quando a operação falha. O cliente não "
        "pode depender dessas assinaturas: qualquer troca de fornecedor contamina o "
        "código. O mesmo vale para código legado: alterar a classe pode ser impossível "
        "ou indesejável, e reimplementar gera duplicação."
    ),
    participantes=(
        "Target: interface que o cliente espera usar",
        "Cliente: usa apenas a interface Target",
        "Adaptee: classe existente com interface incompatível",
        "Adapter: implementa Target e traduz as chamadas para o Adaptee",
    ),
    mecanismo=(
        "O Adapter implementa a interface Target e guarda uma referência ao Adaptee "
        "(Object Adapter, por composição). Quando o cliente chama o método do Target, o "
        "Adapter converte o que for preciso (unidade, tipo de retorno, exceção) e chama "
        "o Adaptee. O cliente só conhece o Target. Não existe Context nem escolha de "
        "algoritmo aqui: o foco é traduzir entre duas interfaces que já existiam."
    ),
    consequencias=(
        "Reutiliza código existente sem modificá-lo",
        "Desacopla o cliente da biblioteca concreta",
        "Object Adapter (composição) acopla menos que Class Adapter (herança)",
        "Custo: introduz uma classe adicional e um nível de indireção",
        "Custo: a adaptação pode ficar superficial se as semânticas forem diferentes",
    ),
    quando_usar=(
        "Precisa usar uma classe existente com interface incompatível",
        "Quer uma classe reutilizável que coopere com classes de interfaces não relacionadas",
        "Integra biblioteca de terceiros ou código legado sem alterá-los",
        "Precisa isolar o sistema de uma API externa que pode mudar",
        "Class Adapter: quando a linguagem permite herança múltipla e você quer herdar do Adaptee",
        "Object Adapter: quando se quer menor acoplamento e o Adaptee é composto, não herdado",
    ),
    quando_evitar=(
        "Você controla o código do Adaptee: nesse caso, mude a interface direto",
        "A incompatibilidade é conceitual, não apenas de assinatura (os modelos de dados "
        "são diferentes; um Adapter só mascara o problema)",
        "Uma camada de adaptação seria usada por um único ponto e por pouco tempo",
    ),
    confusoes={
        "Bridge": (
            "Bridge é projetado desde o início para variar abstração e implementação "
            "independentemente; Adapter corrige depois uma incompatibilidade entre "
            "interfaces já existentes"
        ),
        "Decorator": (
            "Decorator mantém a mesma interface e adiciona responsabilidades; Adapter "
            "muda a interface para torná-la compatível"
        ),
        "Facade": (
            "Facade simplifica o acesso a um subsistema inteiro, criando uma interface "
            "nova; Adapter converte a interface de um único objeto"
        ),
        "Proxy": (
            "Proxy implementa a mesma interface do objeto real e controla o acesso; "
            "Adapter implementa uma interface diferente da do objeto adaptado"
        ),
    },
    sinal_pratico=(
        "Pergunte quando as duas interfaces surgiram. Se ambas já existiam, eram "
        "incompatíveis e o Adapter entrou depois para reconciliá-las, é Adapter. Se "
        "abstração e implementação foram projetadas desde o início como duas hierarquias "
        "independentes, é Bridge."
    ),
    erro_comum=(
        "Criar um Adapter quando o próprio sistema controla a classe adaptada: nesse "
        "caso o correto é alterar a interface original. Outro erro é o Adapter que só "
        "repassa a chamada com o mesmo nome e a mesma assinatura, sem converter nada: "
        "ele não adapta, apenas adiciona indireção."
    ),
    analogia=(
        "um adaptador de tomada: o aparelho espera um plugue (Target), a parede oferece "
        "outro formato (Adaptee), e o adaptador traduz sem alterar nenhum dos dois."
    ),
    gancho=(
        "Comece por duas peças que não encaixam: o sistema quer chamar pagar(reais), mas "
        "cada biblioteca tem outra assinatura. Pergunte ao aluno como o código de vendas "
        "deveria chamar as duas sem ficar cheio de conversões."
    ),
    estrategia=(
        "Integração: mostre duas interfaces já existentes e incompatíveis, e deixe o aluno "
        "descobrir que alguém precisa traduzir entre elas. Foque no que é convertido "
        "(unidade, retorno, exceção). Não fale em Context nem em escolha de algoritmo."
    ),
    progressao=("contexto", "conceito", "problema", "participantes", "exemplo",
                "mecanismo", "quando", "erro", "confusoes", "custos"),
    perguntas={
        "padrao": "Quer ver como isso fica em código ou prefere testar com um exercício?",
        "contexto": "Faz sentido até aqui? Posso detalhar a ideia do Adapter ou, se preferir, mostrar o problema que ele resolve.",
        "conceito": "Quer que eu mostre o problema que ele resolve, para ficar mais concreto?",
        "problema": "Por que não simplesmente editar a classe da biblioteca?",
        "mecanismo": "O que exatamente o adaptador converte quando o cliente chama o método?",
        "participantes": "Entre cliente, adaptador e classe adaptada, quem conhece quem?",
        "custos": "Quando a camada extra de tradução deixa de compensar?",
        "quando": "Se você controla a classe que seria adaptada, o que faria?",
        "confusoes": "Qual pergunta você faria sobre as duas interfaces para saber se é esse padrão?",
        "erro": "Como você perceberia que um adaptador só repassa a chamada sem converter nada?",
        "exemplo": "Se chegasse um terceiro serviço de pagamento, o que você criaria e o que ficaria igual?",
        "fechamento": "Quer praticar com um exercício para fixar esses pontos?",
    },
    exemplo_java="""\
// interface usada pelo cliente
interface MeioPagamento {
    boolean pagar(double reais); // double só para simplificar; em sistemas reais use BigDecimal
}

// biblioteca de cartão (terceiros): centavos na entrada, código na saída
class GatewayCartao {
    int cobrarEmCentavos(long centavos) {
        return centavos > 0 ? 0 : 1; // 0 = aprovado
    }
}

// biblioteca de Pix (terceiros): reais na entrada, exceção em caso de erro
class GatewayPix {
    void enviarPix(double reais) {
        if (reais <= 0) throw new IllegalStateException("valor inválido");
    }
}

// converte unidade (reais -> centavos) e retorno (código -> boolean)
class CartaoAdapter implements MeioPagamento {
    private final GatewayCartao gateway;
    CartaoAdapter(GatewayCartao gateway) { this.gateway = gateway; }
    public boolean pagar(double reais) {
        long centavos = Math.round(reais * 100);
        return gateway.cobrarEmCentavos(centavos) == 0;
    }
}

// converte exceção -> boolean
class PixAdapter implements MeioPagamento {
    private final GatewayPix gateway;
    PixAdapter(GatewayPix gateway) { this.gateway = gateway; }
    public boolean pagar(double reais) {
        try {
            gateway.enviarPix(reais);
            return true;
        } catch (IllegalStateException e) {
            return false;
        }
    }
}

public class Main {
    public static void main(String[] args) {
        MeioPagamento cartao = new CartaoAdapter(new GatewayCartao());
        MeioPagamento pix = new PixAdapter(new GatewayPix());
        System.out.println("Cartão: " + cartao.pagar(150.00));
        System.out.println("Pix: " + pix.pagar(150.00));
    }
}
""",
    uml=(
        "Cliente ──► «interface» MeioPagamento (Target)\n"
        "                  ▲\n"
        "        ┌─────────┴─────────┐\n"
        "  CartaoAdapter        PixAdapter      (Adapters)\n"
        "        │ usa               │ usa\n"
        "  GatewayCartao        GatewayPix      (Adaptees)"
    ),
    o_que_observar=(
        "O cliente (main) só enxerga MeioPagamento. Cada Adapter implementa essa "
        "interface e guarda o gateway por composição. O CartaoAdapter converte a unidade "
        "(reais para centavos) e o retorno (código int para boolean); o PixAdapter "
        "converte exceção em boolean. Nenhuma das duas bibliotecas foi alterada."
    ),
    se_amanha=(
        "Se amanhã entrar um terceiro gateway, basta criar mais um adaptador que "
        "implemente MeioPagamento. A interface, o cliente e os outros adaptadores não "
        "mudam."
    ),
    dominio_exercicio="integração de serviços externos",
    exercicio_fixo=(
        "**Cenário:** Um aplicativo de clima mostra a temperatura chamando "
        "obterTemperaturaCelsius(), que devolve um número com casas decimais. A empresa "
        "contratou um sensor de terceiros, de código fechado, cujo método lerKelvinX10() "
        "devolve um inteiro (Kelvin vezes 10) e lança uma exceção de tempo esgotado. Não "
        "é possível editar o código do sensor.\n\n"
        "**Sua tarefa:** Projete como o aplicativo continua chamando apenas "
        "obterTemperaturaCelsius() e passa a usar o sensor novo. Diga quais classes "
        "existem, o que cada uma conhece e o que precisa ser convertido.\n\n"
        "**Critérios de sucesso:**\n"
        "- O restante do aplicativo não conhece o sensor.\n"
        "- O código do sensor permanece intacto.\n"
        "- Você apontou o que é convertido: unidade, tipo de retorno e tratamento de erro.\n\n"
        "**Para começar:**\n"
        "1. Quem já existia antes e não pode mudar?\n"
        "2. Que peça nova precisaria falar as duas \"línguas\"?\n\n"
        "Responda começando por **Minha resposta:**"
    ),
    termos_proibidos_exercicio=("Strategy", "Context", "Adapter", "Target", "Adaptee"),
    termos_invalidos=("Context",),
    palavras_chave=("adapter", "adaptador"),
    contexto_categoria=("Adapter é estrutural: trata de como classes e objetos já existentes "
                        "se combinam em uma estrutura que funciona."),
    confusao_principal="Bridge",
)

PADROES: dict[str, Padrao] = {"strategy": STRATEGY, "adapter": ADAPTER}

# padrões GoF que o sistema NÃO cobre (para recusar com honestidade)
GOF_FORA = (
    "factory method", "abstract factory", "builder", "prototype", "bridge", "composite",
    "decorator", "facade", "flyweight", "proxy", "command", "iterator", "memento",
    "observer", "state", "visitor", "template method", "singleton", "mediator",
    "chain of responsibility", "interpreter",
)


def fatos_comparacao() -> str:
    return (
        STRATEGY.fatos(["definicao", "participantes"])
        + "\n\n"
        + ADAPTER.fatos(["definicao", "participantes"])
        + "\n\nCONTRASTE: "
        + STRATEGY.confusoes["Adapter"]
        + ". Em Strategy existe Context e a escolha vem do cliente; em Adapter não "
        "existe Context: o objetivo é traduzir uma interface existente para outra."
    )


def renderizar_fatos(padrao: Padrao, intencao: str) -> str:
    """Resposta determinística (fallback) montada só com o conteúdo verificado."""
    t = TOPICOS_POR_INTENCAO.get(intencao, TOPICOS_POR_INTENCAO["conceito"])
    partes: list[str] = []
    if "contexto" in t:
        partes.append(CONTEXTO_GERAL + " " + padrao.contexto_categoria)
    if "definicao" in t:
        partes.append(padrao.definicao)
    if "problema" in t:
        partes.append(padrao.problema)
    if "analogia" in t:
        partes.append("Uma analogia: " + padrao.analogia)
    if "participantes" in t:
        partes.append("Participantes: " + "; ".join(padrao.participantes) + ".")
    if "mecanismo" in t:
        partes.append(padrao.mecanismo)
    if "custos" in t:
        partes.append("Consequências: " + "; ".join(padrao.consequencias) + ".")
    if "usar" in t:
        partes.append("Quando usar: " + "; ".join(padrao.quando_usar) + ".")
    if "evitar" in t:
        partes.append("Quando evitar: " + "; ".join(padrao.quando_evitar) + ".")
    if "confusoes" in t:
        partes.append(
            "Confusões frequentes: "
            + "; ".join(f"{padrao.nome} × {k}: {v}" for k, v in padrao.confusoes.items())
            + ". " + padrao.sinal_pratico
        )
    if "erro" in t:
        partes.append("Erro comum: " + padrao.erro_comum)
    return "\n\n".join(partes) + "\n\n" + padrao.pergunta_final(intencao)

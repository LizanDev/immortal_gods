"""Management command to seed synergy tags and rebalance god rarities."""

from django.core.management.base import BaseCommand

from apps.gods.models import God, GodSynergyTag, Rarity


SYNERGY_TAGS_DATA: dict[str, list[str]] = {
    "Nuwa": ['creation', 'magic'],
    "Ymir": ['creation', 'strength', 'sea'],
    "Hades": ['death', 'king'],
    "Persephone": ['death', 'nature'],
    "Mictlantecuhtli": ['death', 'king'],
    "Zhong Kui": ['death', 'guardian'],
    "Osiris": ['death', 'king'],
    "Anubis": ['death', 'guardian'],
    "Hel": ['death', 'king'],
    "Gaia": ['earth', 'creation'],
    "Xipe Totec": ['earth', 'healing'],
    "Coatlicue": ['earth', 'death'],
    "Frigg": ['family', 'fate'],
    "Morpheus": ['fate', 'magic'],
    "Hephaestus": ['forge', 'earth'],
    "Prometheus": ['forge', 'fate'],
    "Xiuhtecuhtli": ['forge', 'sun'],
    "Ptah": ['forge', 'creation'],
    "Heimdall": ['guardian', 'messenger'],
    "Shennong": ['healing', 'nature'],
    "Xiwangmu": ['healing', 'guardian'],
    "Artemis": ['hunt', 'moon'],
    "Skadi": ['hunt', 'earth'],
    "Ullr": ['hunt', 'messenger'],
    "Ma'at": ['justice', 'fate'],
    "Cronus": ['king', 'strength'],
    "Jade Emperor": ['king', 'sky'],
    "Huangdi": ['king', 'war', 'forge'],
    "Amun": ['king', 'sky'],
    "Eros": ['love', 'trickery'],
    "Xochiquetzal": ['love', 'nature'],
    "Bastet": ['love', 'guardian'],
    "Hathor": ['love', 'family'],
    "Freya": ['love', 'magic'],
    "Hecate": ['magic', 'moon'],
    "Isis": ['magic', 'healing'],
    "Hermes": ['messenger', 'trickery'],
    "Ehecatl": ['messenger', 'sky'],
    "Coyolxauhqui": ['moon', 'war'],
    "Chang'e": ['moon', 'love'],
    "Demeter": ['nature', 'wealth', 'family'],
    "Dionysus": ['nature', 'magic'],
    "Sif": ['nature', 'family'],
    "Poseidon": ['sea', 'earth'],
    "Dragon King": ['sea', 'king', 'wealth'],
    "Njord": ['sea', 'wealth'],
    "Zeus": ['sky', 'thunder', 'family'],
    "Horus": ['sky', 'war'],
    "Sobek": ['strength', 'sea', 'wealth'],
    "Vidar": ['strength', 'earth'],
    "Apollo": ['sun', 'wisdom'],
    "Tonatiuh": ['sun', 'strength'],
    "Ra": ['sun', 'king', 'thunder'],
    "Khepri": ['sun', 'creation'],
    "Baldr": ['sun', 'healing'],
    "Tlaloc": ['thunder', 'nature'],
    "Lei Gong": ['thunder', 'justice'],
    "Thor": ['thunder', 'strength'],
    "Tezcatlipoca": ['trickery', 'fate'],
    "Sun Wukong": ['trickery', 'strength'],
    "Set": ['trickery', 'strength'],
    "Loki": ['trickery', 'magic'],
    "Athena": ['war', 'wisdom', 'justice'],
    "Ares": ['war', 'strength'],
    "Nike": ['war', 'messenger'],
    "Huitzilopochtli": ['war', 'sun'],
    "Nezha": ['war', 'strength'],
    "Erlang Shen": ['war', 'wisdom'],
    "Guan Yu": ['war', 'justice'],
    "Sekhmet": ['war', 'strength'],
    "Tyr": ['war', 'justice'],
    "Caishen": ['wealth', 'fate'],
    "Quetzalcoatl": ['wisdom', 'sky'],
    "Fuxi": ['wisdom', 'fate'],
    "Thoth": ['wisdom', 'messenger', 'moon'],
    "Seshat": ['wisdom', 'fate'],
    "Odin": ['wisdom', 'king', 'hunt'],
    "Bragi": ['wisdom', 'magic'],
}

RARITY_REBALANCE: dict[str, str] = {
    "Amun": Rarity.MYTHIC,
    "Anubis": Rarity.EPIC,
    "Apollo": Rarity.EPIC,
    "Ares": Rarity.EPIC,
    "Artemis": Rarity.RARE,
    "Athena": Rarity.EPIC,
    "Baldr": Rarity.RARE,
    "Bastet": Rarity.COMMON,
    "Bragi": Rarity.RARE,
    "Caishen": Rarity.COMMON,
    "Chang'e": Rarity.RARE,
    "Coatlicue": Rarity.LEGENDARY,
    "Coyolxauhqui": Rarity.RARE,
    "Cronus": Rarity.LEGENDARY,
    "Demeter": Rarity.COMMON,
    "Dionysus": Rarity.EPIC,
    "Dragon King": Rarity.LEGENDARY,
    "Ehecatl": Rarity.EPIC,
    "Erlang Shen": Rarity.EPIC,
    "Eros": Rarity.RARE,
    "Freya": Rarity.EPIC,
    "Frigg": Rarity.RARE,
    "Fuxi": Rarity.LEGENDARY,
    "Gaia": Rarity.LEGENDARY,
    "Guan Yu": Rarity.EPIC,
    "Hades": Rarity.LEGENDARY,
    "Hathor": Rarity.LEGENDARY,
    "Hecate": Rarity.LEGENDARY,
    "Heimdall": Rarity.EPIC,
    "Hel": Rarity.LEGENDARY,
    "Hephaestus": Rarity.RARE,
    "Hermes": Rarity.RARE,
    "Horus": Rarity.EPIC,
    "Huangdi": Rarity.LEGENDARY,
    "Huitzilopochtli": Rarity.MYTHIC,
    "Isis": Rarity.EPIC,
    "Jade Emperor": Rarity.MYTHIC,
    "Khepri": Rarity.LEGENDARY,
    "Lei Gong": Rarity.EPIC,
    "Loki": Rarity.LEGENDARY,
    "Ma'at": Rarity.EPIC,
    "Mictlantecuhtli": Rarity.EPIC,
    "Morpheus": Rarity.COMMON,
    "Nezha": Rarity.EPIC,
    "Nike": Rarity.RARE,
    "Njord": Rarity.LEGENDARY,
    "Nuwa": Rarity.LEGENDARY,
    "Odin": Rarity.MYTHIC,
    "Osiris": Rarity.LEGENDARY,
    "Persephone": Rarity.EPIC,
    "Poseidon": Rarity.LEGENDARY,
    "Prometheus": Rarity.LEGENDARY,
    "Ptah": Rarity.COMMON,
    "Quetzalcoatl": Rarity.LEGENDARY,
    "Ra": Rarity.LEGENDARY,
    "Sekhmet": Rarity.RARE,
    "Seshat": Rarity.RARE,
    "Set": Rarity.RARE,
    "Shennong": Rarity.LEGENDARY,
    "Sif": Rarity.EPIC,
    "Skadi": Rarity.RARE,
    "Sobek": Rarity.EPIC,
    "Sun Wukong": Rarity.LEGENDARY,
    "Tezcatlipoca": Rarity.LEGENDARY,
    "Thor": Rarity.LEGENDARY,
    "Thoth": Rarity.RARE,
    "Tlaloc": Rarity.EPIC,
    "Tonatiuh": Rarity.RARE,
    "Tyr": Rarity.EPIC,
    "Ullr": Rarity.EPIC,
    "Vidar": Rarity.COMMON,
    "Xipe Totec": Rarity.EPIC,
    "Xiuhtecuhtli": Rarity.EPIC,
    "Xiwangmu": Rarity.LEGENDARY,
    "Xochiquetzal": Rarity.RARE,
    "Ymir": Rarity.LEGENDARY,
    "Zeus": Rarity.MYTHIC,
    "Zhong Kui": Rarity.RARE,
}

GOD_LORE: dict[str, str] = {
    # Greek
    "Zeus": (
        "Rey del Olimpo y dios del cielo, el trueno y la justicia. "
        "Gobernante supremo del panteón griego, hijo de Cronos y Rea, "
        "lideró a los olímpicos en la Titanomaquia para derrocar a su padre."
    ),
    "Hades": (
        "Dios del inframundo y los muertos. Gobernante del Érebo, "
        "poseía el casco de invisibilidad y era temido incluso por sus "
        "hermanos. Secuestró a Perséfone para convertirla en su reina."
    ),
    "Poseidon": (
        "Dios del mar, los terremotos y los caballos. Portador del tridente, "
        "era conocido por su temperamento volátil. Creó al caballo de la espuma del mar."  # noqa: E501
    ),
    "Athena": (
        "Diosa de la sabiduría, la estrategia y la artesanía. Nació de la cabeza de Zeus "  # noqa: E501
        "completamente armada. Patrona de Atenas, inventó el olivo y la flauta."
    ),
    "Apollo": (
        "Dios del sol, la música, la poesía y la profecía. Conducía el carro solar "
        "por el cielo. Hermano gemelo de Artemisa, su oráculo en Delfos era el más "
        "importante del mundo griego."
    ),
    "Ares": (
        "Dios de la guerra y la violencia. Hijo de Zeus y Hera, representaba "
        "el aspecto más brutal del combate. Acompañado por Fobos (miedo) y Deimos (terror) "  # noqa: E501
        "en el campo de batalla."
    ),
    "Artemis": (
        "Diosa de la caza, la luna y la naturaleza salvaje. Hermana gemela de Apolo, "
        "protectora de los jóvenes y los animales. Portaba arco de plata y flechas mágicas."  # noqa: E501
    ),
    "Hermes": (
        "Mensajero de los dioses, dios de los viajeros, el comercio y los ladrones. "
        "Portaba sandalias aladas y el caduceo. Guiaba las almas al inframundo."
    ),
    "Hephaestus": (
        "Dios del fuego, la forja y la artesanía. Herrero divino del Olimpo, "
        "creó las armas de los dioses y el escudo de Aquiles. Era cojo de nacimiento "
        "y estaba casado con Afrodita."
    ),
    "Demeter": (
        "Diosa de la agricultura, la cosecha y la fertilidad. Madre de Perséfone, "
        "su tristeza cuando Hades secuestró a su hija causó el invierno eterno."
    ),
    "Dionysus": (
        "Dios del vino, el éxtasis y el teatro. Hijo de Zeus y Sémele, "
        "vagó por el mundo enseñando el cultivo de la vid. Sus seguidoras, "
        "las ménades, caían en trance durante sus rituales."
    ),
    "Persephone": (
        "Reina del inframundo y diosa de la primavera. Hija de Deméter y Zeus, "
        "pasa seis meses con Hades (otoño/invierno) y seis con su madre (primavera/verano)."  # noqa: E501
    ),
    "Hecate": (
        "Diosa de la magia, la brujería y los cruces de caminos. Poseía tres formas "
        "y portaba antorchas. Acompañaba a Perséfone en el inframundo."
    ),
    "Eros": (
        "Dios del amor y el deseo. Hijo de Afrodita y Ares, sus flechas doradas "
        "causaban amor y las de plomo indiferencia. Representado como un joven alado."
    ),
    "Nike": (
        "Diosa de la victoria. Portaba alas y una corona de laurel. "
        "Acompañaba a Atenea en las batallas y era representada en las monedas "
        "griegas como símbolo de triunfo."
    ),
    "Cronus": (
        "Titán del tiempo y la cosecha. Padre de Zeus y los olímpicos, "
        "devoró a sus hijos por miedo a ser derrocado. Eventualmente Zeus lo "
        "derrotó y lo encerró en el Tártaro."
    ),
    "Gaia": (
        "Diosa primordial de la Tierra. Madre de los titanes, cíclopes y gigantes. "
        "Emergió del Caos y dio a luz a Urano (el cielo) sin necesidad de pareja."
    ),
    "Prometheus": (
        "Titán protector de la humanidad. Robó el fuego divino del Olimpo para "
        "entregarlo a los mortales, por lo que Zeus lo encadenó a una roca donde "
        "un águila devoraba su hígado cada día."
    ),
    "Morpheus": (
        "Dios de los sueños. Hijo de Hipnos (el sueño), podía tomar cualquier "
        "forma humana en los sueños. Aparecía en los sueños proféticos para "
        "entregar mensajes de los dioses."
    ),
    # Aztec
    "Huitzilopochtli": (
        "Dios principal de los mexicas, deidad del sol y la guerra. "
        "Guió al pueblo azteca desde Aztlán hasta el Valle de México, "
        "indicando el lugar para fundar Tenochtitlán donde un águila devoraba una serpiente."  # noqa: E501
    ),
    "Quetzalcoatl": (
        "Dios del viento, la sabiduría y la creación. La Serpiente Emplumada, "
        "creó a la humanidad moliendo huesos del inframundo con su sangre. "
        "Gobernó como rey-sacerdote en Tollan."
    ),
    "Tezcatlipoca": (
        "Dios del cielo nocturno, la providencia y la hechicería. Espejo Humeante, "
        "era omnipresente y omnipotente. Hermano de Quetzalcóatl, representaba "
        "el caos y el cambio."
    ),
    "Tlaloc": (
        "Dios de la lluvia, el relámpago y la fertilidad. Proveía la lluvia "
        "necesaria para las cosechas, pero también enviaba granizo y tormentas. "
        "Su paraíso, Tlalocan, acogía a los ahogados."
    ),
    "Xipe Totec": (
        "Dios de la primavera, la regeneración y los orfebres. Nuestro Señor Desollado, "  # noqa: E501
        "se despojaba de su piel para alimentar a la humanidad, simbolizando la "
        "renovación de la tierra."
    ),
    "Coatlicue": (
        "Diosa de la tierra, la fertilidad y la muerte. Madre de Huitzilopochtli y "
        "la luna Coyolxauhqui. Vestía una falda de serpientes y un collar de corazones humanos."  # noqa: E501
    ),
    "Mictlantecuhtli": (
        "Dios de la muerte y rey del Mictlán, el inframundo azteca. "
        "Se representaba como un esqueleto con sangre. Regía los nueve niveles "
        "del inframundo junto a su esposa Mictecacíhuatl."
    ),
    "Xochiquetzal": (
        "Diosa del amor, la belleza, las flores y las artes. Patrona de los "
        "artesanos y las cortesanas. Esposa de Tlaloc, residía en Tamoanchan, "
        "el paraíso florido."
    ),
    "Xiuhtecuhtli": (
        "Dios del fuego, el calor y el tiempo. Señor del Turquesa, "
        "era el dios más antiguo del panteón azteca. El fuego siempre ardía "
        "en su honor, y las cenizas se usaban en rituales."
    ),
    "Coyolxauhqui": (
        "Diosa de la luna. Hija de Coatlicue, lideró a sus hermanos en un ataque "
        "contra Huitzilopochtli, quien la derrotó y desmembró, lanzando su cuerpo "
        "a la luna. Su mito explica el ciclo lunar."
    ),
    "Ehecatl": (
        "Dios del viento. Manifestación de Quetzalcóatl, soplaba para mover "
        "el sol y la lluvia. Su templo circular permitía al viento fluir "
        "sin obstáculos."
    ),
    "Tonatiuh": (
        "Dios del sol. Gobernaba la era actual, el Quinto Sol. Exigía "
        "corazones humanos como ofrenda para mantener su movimiento "
        "a través del cielo."
    ),
    # Chinese
    "Jade Emperor": (
        "Emperador de Jade, gobernante supremo del cielo y la tierra en la "
        "mitología china. Originado como un príncipe mortal que alcanzó la "
        "inmortalidad tras incontables pruebas. Presidía sobre todos los dioses "
        "y espíritus desde el Palacio Celestial."
    ),
    "Sun Wukong": (
        "Rey Mono, nacido de una piedra celestial. Obtuvo inmortalidad y "
        "poderes divinos tras estudiar con un maestro taoísta. Portaba el "
        "Báculo de Oro, podía transformarse en 72 formas y viajar en una nube."
    ),
    "Nezha": (
        "Príncipe niño guerrero. Nació dentro de una flor de loto tras tres "
        "años de gestación. Derrotó al Dragón Rey del Mar Este, "
        "usaba el Lazo Universal y las Ruedas de Viento."
    ),
    "Erlang Shen": (
        "Dios guerrero con un tercer ojo en la frente. Portaba una lanza "
        "de tres puntas y estaba acompañado por su perro celestial. "
        "Capturó a Sun Wukong durante su rebelión en el cielo."
    ),
    "Chang'e": (
        "Diosa de la luna. Bebió el elixir de la inmortalidad para evitar "
        "que cayera en manos malvadas y flotó hasta la luna, "
        "donde habita eternamente con el Conejo de Jade."
    ),
    "Dragon King": (
        "Rey Dragón de los Cuatro Mares. Controlaba las lluvias, los ríos "
        "y el clima. Vivía en un palacio submarino de cristal, "
        "y su hija fue rescatada por Nezha."
    ),
    "Guan Yu": (
        "Dios de la guerra, la lealtad y la justicia. General histórico "
        "del período de los Tres Reinos, deificado tras su muerte. "
        "Portaba el legendario Dragón Verde de hoja ancha."
    ),
    "Nuwa": (
        "Diosa creadora de la humanidad. Moldeó a los primeros humanos "
        "con arcilla amarilla. Cuando el cielo colapsó, reparó el vacío "
        "con cinco piedras de colores fundidas."
    ),
    "Zhong Kui": (
        "Cazador de demonios y dios de la exorcización. Tras suicidarse "
        "por una injusticia, el Emperador de Jade lo nombró líder de los "
        "espíritus cazadores del inframundo."
    ),
    "Caishen": (
        "Dios de la riqueza y la prosperidad. Traía fortuna y abundancia "
        "a quienes lo veneraban. Representado con una túnica roja y un "
        "lingote de oro en la mano."
    ),
    "Fuxi": (
        "Primer emperador legendario, creador de la civilización china. "
        "Enseñó la caza, la pesca y la escritura. Creó los Ocho Trigramas "
        "del I Ching observando los patrones del universo."
    ),
    "Shennong": (
        "Emperador divino de la agricultura y la medicina. Probó cientos "
        "de hierbas para descubrir sus propiedades curativas, "
        "envenenándose 70 veces al día. Enseñó el cultivo del arroz."
    ),
    "Xiwangmu": (
        "Reina Madre de Occidente. Vivía en las montañas Kunlun y poseía "
        "los melocotones de la inmortalidad. Podía conceder la vida eterna "
        "a los mortales dignos."
    ),
    "Huangdi": (
        "Emperador Amarillo, ancestro legendario de todos los chinos. "
        "Inventó la brújula, el calendario y la escritura. Derrotó a Chi You "
        "unificando las tribus bajo su mandato."
    ),
    "Lei Gong": (
        "Dios del trueno. Portaba un martillo y un cincel para crear "
        "rayos. Castigaba a los malvados y a los espíritus demoníacos. "
        "Su esposa era la diosa del relámpago."
    ),
    # Egyptian
    "Ra": (
        "Dios del sol y rey de los dioses egipcios. Viajaba diariamente "
        "en su barca solar por el cielo, luchando contra la serpiente "
        "Apofis cada noche. Fue el primer gobernante de Egipto."
    ),
    "Osiris": (
        "Dios de la muerte, la resurrección y la fertilidad. Asesinado por "
        "su hermano Set y resucitado por Isis, se convirtió en juez de "
        "los muertos en el Duat. Simboliza el ciclo de la vida."
    ),
    "Anubis": (
        "Dios de la momificación y guía de las almas al más allá. "
        "Con cabeza de chacal, supervisaba el pesaje del corazón contra "
        "la pluma de Maat en el juicio de los muertos."
    ),
    "Horus": (
        "Dios del cielo y la realeza. Hijo de Osiris e Isis, vengó la "
        "muerte de su padre luchando contra Set. Perdió un ojo en la "
        "batalla, que se convirtió en el poderoso Ojo de Horus."
    ),
    "Isis": (
        "Diosa de la magia, la maternidad y la curación. Esposa de Osiris, "
        "reconstruyó su cuerpo desmembrado y concibió a Horus. Era la "
        "diosa más venerada, conocida como la Gran Hechicera."
    ),
    "Set": (
        "Dios del caos, la violencia y el desierto. Asesinó a su hermano "
        "Osiris por celos. Con cabeza de una criatura desconocida, "
        "representaba las fuerzas del mal que amenazaban el orden divino."
    ),
    "Thoth": (
        "Dios de la sabiduría, la escritura y el conocimiento. Inventor "
        "de la escritura jeroglífica, escriba de los dioses. Con cabeza "
        "de ibis, registraba el resultado del juicio de las almas."
    ),
    "Sekhmet": (
        "Diosa de la guerra y la destrucción. Con cabeza de leona, "
        "era la mirada ardiente de Ra. Enviada para castigar a la "
        "humanidad, casi la extinguió hasta que Ra la engañó con cerveza roja."
    ),
    "Bastet": (
        "Diosa de los gatos, la protección y el hogar. Protectora del "
        "bajo Egipto, representaba la dulzura y la fertilidad. "
        "Los gatos eran sagrados en su honor."
    ),
    "Ptah": (
        "Dios creador de Menfis, patrón de los artesanos y arquitectos. "
        "Creó el universo con su palabra y su corazón. Considerado el "
        "padre de la civilización egipcia."
    ),
    "Amun": (
        "Rey de los dioses tebanos. Dios del aire y la creación invisible. "
        "Durante el Imperio Nuevo se convirtió en Amun-Ra, la deidad "
        "suprema del panteón egipcio."
    ),
    "Hathor": (
        "Diosa del amor, la música y la alegría. Representada como vaca "
        "o mujer con cuernos de vaca. Recibía a las almas en el más allá "
        "con comida y bebida."
    ),
    "Khepri": (
        "Dios del sol naciente. Representado como un escarabajo "
        "pelotero empujando el sol por el horizonte. Simbolizaba la "
        "creación, la renovación y la resurrección."
    ),
    "Ma'at": (
        "Diosa de la justicia, la verdad y el orden cósmico. Su pluma "
        "se usaba para pesar los corazones en el juicio de los muertos. "
        "Representaba el equilibrio fundamental del universo."
    ),
    "Sobek": (
        "Dios del Nilo, los cocodrilos y la fertilidad. Con cabeza de "
        "cocodrilo, protegía al faraón y al ejército. Vivía en los "
        "pantanos de Kom Ombo."
    ),
    "Seshat": (
        "Diosa de la escritura, la medición y la arquitectura. Ayudaba "
        "al faraón a diseñar templos y registrar las cosechas. "
        "Escribía los anales reales en hojas de palma."
    ),
    # Nordic
    "Odin": (
        "Padre de todos, dios de la sabiduría, la guerra y la muerte. "
        "Sacrificó un ojo por la sabiduría eterna. Presidía el Valhalla "
        "desde su trono Hlidskjalf, acompañado de sus cuervos Huginn y Muninn."
    ),
    "Thor": (
        "Dios del trueno, la fuerza y la protección. Hijo de Odín, "
        "portaba el martillo Mjolnir que solo él podía levantar. "
        "Defendía Midgard de los gigantes con su cinturón de fuerza."
    ),
    "Loki": (
        "Dios de la travesura y el caos. Hijo de gigantes, hermano "
        "de sangre de Odín. Causó la muerte de Baldr y en el Ragnarök "
        "liderará a los gigantes contra los dioses."
    ),
    "Freya": (
        "Diosa del amor, la belleza y la fertilidad. Líder de las "
        "Valkirias, recibía la mitad de los caídos en su campo Folkvangr. "
        "Portaba el collar Brísingamen y un manto de plumas de halcón."
    ),
    "Tyr": (
        "Dios de la guerra, la justicia y los juramentos. Perdió su mano "
        "al colocarla en la boca del lobo Fenrir como garantía. "
        "El dios más valiente del panteón nórdico."
    ),
    "Heimdall": (
        "Guardián de los dioses, vigilante del puente Bifröst. Poseía "
        "oído y vista sobrenaturales. Tocará el cuerno Gjallarhorn "
        "para anunciar el comienzo del Ragnarök."
    ),
    "Frigg": (
        "Reina de los dioses, diosa del matrimonio y la profecía. "
        "Esposa de Odín, conocía el destino pero no lo revelaba. "
        "Lloró la muerte de su hijo Baldr."
    ),
    "Baldr": (
        "Dios de la luz, la belleza y la bondad. Hijo de Odín y Frigg, "
        "era inmune a todo daño excepto al muérdago. Su muerte a manos "
        "de Loki desencadenó el Ragnarök."
    ),
    "Skadi": (
        "Diosa del invierno, la caza y las montañas. Hija del gigante "
        "Thjazi, eligió a Njord como esposo entre los dioses. "
        "Recorría las montañas con esquís y arco."
    ),
    "Vidar": (
        "Dios de la venganza y el silencio. Hijo de Odín, sobrevivirá "
        "al Ragnarök. Vengó la muerte de su padre matando al lobo "
        "Fenrir desgarrándole las fauces."
    ),
    "Ymir": (
        "Gigante primordial del hielo. De su cuerpo los dioses crearon "
        "el mundo: su carne la tierra, su sangre los mares, sus huesos "
        "las montañas y su cráneo el cielo."
    ),
    "Hel": (
        "Diosa de la muerte, reina de Helheim. Hija de Loki, su rostro "
        "era mitad hermoso y mitad putrefacto. Recibía las almas de "
        "quienes no morían en batalla."
    ),
    "Njord": (
        "Dios del mar, el viento y la riqueza. Padre de Freyr y Freya, "
        "controlaba las tormentas y la pesca. Su palacio Noatun estaba "
        "junto al mar."
    ),
    "Sif": (
        "Diosa de la fertilidad y la tierra. Esposa de Thor, conocida "
        "por su larga cabellera dorada que Loki cortó como broma. "
        "Los enanos forjaron cabello nuevo de oro puro."
    ),
    "Ullr": (
        "Dios de la caza, el esquí y el tiro con arco. Hijastro de Thor, "
        "era un arquero incomparable y patinador sobre hielo. "
        "Gobernaba Asgard durante el invierno."
    ),
    "Bragi": (
        "Dios de la poesía, la elocuencia y la música. Esposo de Idun, "
        "recibía a los héroes en el Valhalla con poemas. "
        "Su lengua estaba grabada con runas de sabiduría."
    ),
}


class Command(BaseCommand):
    """Seed synergy tags and rebalance rarities."""

    help = "Assigns synergy tags and rebalances rarities for all gods"

    def handle(self, *args, **options):
        self.stdout.write("Rebalancing god rarities...")
        updated = 0
        for name, rarity in RARITY_REBALANCE.items():
            count = God.objects.filter(name=name).update(rarity=rarity)
            if count:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} god rarities"))

        self.stdout.write("Seeding lore descriptions...")
        lore_updated = 0
        for name, lore in GOD_LORE.items():
            count = God.objects.filter(name=name).update(description=lore)
            if count:
                lore_updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Updated {lore_updated} god descriptions with lore")
        )

        self.stdout.write("Seeding synergy tags...")
        GodSynergyTag.objects.all().delete()
        tags_created = 0
        for name, tags in SYNERGY_TAGS_DATA.items():
            try:
                god = God.objects.get(name=name)
            except God.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  God '{name}' not found, skipping")
                )
                continue
            for tag in tags:
                GodSynergyTag.objects.get_or_create(god=god, tag=tag)
                tags_created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {tags_created} synergy tags"
                f" for {len(SYNERGY_TAGS_DATA)} gods"
            )
        )

import './App.css';
import React, { useState, useEffect } from 'react';

function CardPreview({selectedCard}) {
  const imagePath = `./images/${selectedCard.id}.jpg`;
  return (
    <div className="cardPreview">
      <img className="bigCard" src={require(`${imagePath}`)} alt="card"></img>
    </div>
  )
}

function CardEffect({selectedCard}) {
  return (
    <>
      <fieldset className="panelSection cardEffect">
          <legend className="boxTitle">Card Effect</legend>
          <div className="cardEffectInformation">
            <span>{selectedCard.desc}</span>
          </div>
      </fieldset>
    </>
  )
}

function CardInformation({selectedCard, selectedCardLocation, clickHandler}) {
  return (
    <>
      <fieldset className="panelSection cardInformation">
          <legend className="boxTitle">Card Information</legend>
          {selectedCard && <StatInformation clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation}></StatInformation>}
          {selectedCard && <PositionInformation clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation}></PositionInformation>}
          {selectedCard && <AttackInformation clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation}></AttackInformation>}
      </fieldset>
    </>
  )
}

function CardActions({selectedCard, selectedCardLocation, clickHandler, summonableCards, activatableCards, attackers, settableCards}) {
  return (
    <>
    <fieldset className="panelSection cardActions">
      <legend className="boxTitle">Card Actions</legend>
      {selectedCard && <SummonInformation clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation} summonableCards={summonableCards}></SummonInformation>}
      {selectedCard && <ActivateInformation clickHandler={clickHandler} selectedCard={selectedCard} activatableCards={activatableCards} selectedCardLocation={selectedCardLocation}></ActivateInformation>}
      {selectedCard && <AttackActions clickHandler={clickHandler} selectedCard={selectedCard} attackers={attackers}></AttackActions>}
      {selectedCard && <SetInformation clickHandler={clickHandler} selectedCard={selectedCard} settableCards={settableCards}></SetInformation>}
    </fieldset>
    </>
  )
}

function ActivateInformation({selectedCard, clickHandler, activatableCards, selectedCardLocation}) {
  if (activatableCards === [] || activatableCards === undefined) {
    return (
      <>
      <div className="activateInformation">
        <span className="bubbleMain">Activate</span>
        <span className="bubble">Cannot Activate</span>
      </div>
      </>
    )
  }

  if (selectedCard.type !== "monster") {
    if (activatableCards.map(card => card.name).includes(selectedCard.name)) {
      return (
        <>
          <div className="activateInformation">
            <span className="bubbleMain">Activate</span>
            {selectedCardLocation.includes("H") && <span onClick={() => clickHandler({"activate": {"card": selectedCard, "zone": []}})} className="bubble">Confirm</span>}
            {!selectedCardLocation.includes("H") && <span onClick={() => clickHandler({"activate": {"card": selectedCard, "zone": selectedCardLocation}})} className="bubble">Confirm</span>}
          </div>
        </>
        )
    }
  return (
    <>
    <div className="activateInformation">
      <span className="bubbleMain">Activate</span>
      <span className="bubble">Cannot Activate</span>
    </div>
    </>
  )
  }
}

function SetInformation({selectedCard, selectedCardLocation, clickHandler, settableCards}) {
  if (settableCards === [] || settableCards === undefined) {
    return (
      <>
      <div className="activateInformation">
        <span className="bubbleMain">Set</span>
        <span className="bubble">Cannot Set</span>
      </div>
      </>
    )
  }

  if (selectedCard.type === "spell" || selectedCard.type === "trap") {
    if (settableCards.map(card => card.global_id).includes(selectedCard.global_id)) {
      return (
        <>
          <div className="activateInformation">
            <span className="bubbleMain">Set</span>
            {selectedCard["other_type"] !== "Field" && <span onClick={() => clickHandler({"set": {"card": selectedCard, "zone": []}})} className="bubble">Confirm</span>}
            {selectedCard["other_type"] === "Field" && <span onClick={() => clickHandler({"set": {"card": selectedCard, "zone": "FZ"}})} className="bubble">Confirm</span>}
          </div>
        </>
        )
    }
  return (
    <>
    <div className="activateInformation">
      <span className="bubbleMain">Set</span>
      <span className="bubble">Cannot Set</span>
    </div>
    </>
  )
  }
}

function SummonInformation({selectedCard, selectedCardLocation, clickHandler, summonableCards}) {
  if (summonableCards === [] || summonableCards === undefined) {
    return (
      <>
      <div className="summonInformation">
        <span className="bubbleMain">Summon</span>
        <span className="bubble">Cannot Summon</span>
      </div>
      </>
    )
  }
  if (selectedCard.type !== "spell" && selectedCard.type !== "trap") {
    if (selectedCard && selectedCard.card_type && selectedCard.card_type.includes("Synchro")) {
      if (summonableCards.map(card => card[1].global_id).includes(selectedCard.global_id)) {
        return (
        <>
          <div className="summonInformation">
            <span className="bubbleMain">Summon (Attack)</span>
            {<span onClick={() => clickHandler({"extra_summon": {"card": selectedCard, "zone": [], "material": null, "position": true}})} className="bubble">Synchro Summon</span>}
          </div>
          <div className="summonInformation">
            <span className="bubbleMain">Summon (Defense)</span>
            {<span onClick={() => clickHandler({"extra_summon": {"card": selectedCard, "zone": [], "material": null, "position": false}})} className="bubble">Synchro Summon</span>}
          </div>
        </>
        )
      }
    }
    if (summonableCards.map(card => card[1].global_id).includes(selectedCard.global_id)) {
      return (
        <>
          <div className="summonInformation">
            <span className="bubbleMain">Summon</span>
            {selectedCard.level <= 4 && <span onClick={() => clickHandler({"perform_summon": {"card": selectedCard, "zone": [], "tributes": null, "set": false}})} className="bubble">Normal Summon</span>}
            {selectedCard.level > 4 && <span onClick={() => clickHandler({"perform_summon": {"card": selectedCard, "zone": [], "tributes": [], "set": false}})} className="bubble">Tribute Summon</span>}
          </div>
          <div className="summonInformation">
          <span className="bubbleMain">Summon</span>
          {selectedCard.level <= 4 && <span onClick={() => clickHandler({"perform_summon": {"card": selectedCard, "zone": [], "tributes": null, "set": true}})} className="bubble">Normal Set</span>}
          {selectedCard.level > 4 && <span onClick={() => clickHandler({"perform_summon": {"card": selectedCard, "zone": [], "tributes": [], "set": true}})} className="bubble">Tribute Set</span>}
          </div>
        </>
        )
    }
  return (
    <>
    <div className="summonInformation">
      <span className="bubbleMain">Summon</span>
      <span className="bubble">Cannot Summon</span>
    </div>
    </>
  )
  }
}

function PositionInformation({selectedCard, selectedCardLocation, clickHandler}) {;
  const imagePath = `./images/${selectedCard.id}.jpg`;

  function positionJson(type) {
    return {"position": [type, selectedCard, selectedCardLocation]}
  }

  if (selectedCard.type === "monster" || selectedCard.type === "xyz_monster") {
    return (
      <>
        <div className="positionInformation">
          <span className="bubbleMain">Position</span>
          <img onClick={() => clickHandler(positionJson("attack"))} title="Attack Position" className={`cardPosition ${selectedCard.position !== "attack" ? "deselected" : ""}`} 
          src={require(`${imagePath}`)} alt="card_position"></img>
          <img onClick={() => clickHandler(positionJson("defense"))} title="Defense Position" className={`cardPosition defenseCard ${selectedCard.position !== "defense" ? "deselected" : ""}`} 
          src={require(`${imagePath}`)} alt="card_position"></img>
          <img onClick={() => clickHandler(positionJson("set"))} title="Face-down Defense Position" className={`cardPosition defenseCard ${selectedCard.position !== "set" ? "deselected" : ""}`} 
          src={require("./images/back.jpg")} alt="card_position"></img>
        </div>
      </>
    )
  } else if (selectedCard.type === "link_monster") {
    return (
      <>
        <div className="positionInformation">
          <span className="bubbleMain">Position</span>
          <img title="Attack Position (Link Monsters cannot be in Defense Position)" className={"cardPosition"} src={require(`${imagePath}`)} alt="card_position"></img>
        </div>
      </>
    )

  } else {
    return (
      <>
        <div className="positionInformation">
          <span className="bubbleMain">Position</span>
          <img onClick={() => clickHandler(positionJson("faceup"))} title="Face-up" className={`cardPosition ${selectedCard.position !== "faceup" ? "deselected" : ""}`} 
          src={require(`${imagePath}`)} alt="card_position"></img>
          <img onClick={() => clickHandler(positionJson("set"))} title="Set" className={`cardPosition ${selectedCard.position !== "set" ? "deselected" : ""}`} 
          src={require("./images/back.jpg")} alt="card_position"></img>
        </div>
      </>
    )
  }
}

function AttackInformation({selectedCard, selectedCardLocation, clickHandler, attackers}) {
  if (selectedCard.type !== "trap" && selectedCard.type !== "spell") {
    return (
      <>
        <div className="statInformation">
          <span className="bubbleMain">Avaliable Attacks</span>
          {selectedCard.position === "attack" && <span title="Remaining Attacks" className="bubble">{selectedCard.attacks}</span>}
          {selectedCard.position === "defense" && <span title="Monsters cannot Attack in Defense Position" className="bubble">0</span>}
          {selectedCard.position === "set" && <span title="Monsters cannot Attack in Face-down Defense Position" className="bubble">0</span>}
        </div>
      </>
    )
  } else {
    return (
      <>
        <>
        <div className="statInformation">
          <span className="bubbleMain">Avaliable Attacks</span>
          <span className="bubble" title="This Card cannot Attack">0</span>
        </div>
      </>
      </>
    )
  }
}

function AttackActions({selectedCard, selectedCardLocation, clickHandler, attackers}) {
  if (attackers === [] || attackers === undefined) {
    return (
      <>
      <div className="activateInformation">
        <span className="bubbleMain">Attack</span>
        <span className="bubble">Cannot Attack</span>
      </div>
      </>
    )
  }

  if (selectedCard.type !== "spell" && selectedCard.type !== "trap") {
    if (attackers.map(card => card.name).includes(selectedCard.name)) {
      return (
        <>
          <div className="activateInformation">
            <span className="bubbleMain">Attack</span>
            <span onClick={() => clickHandler({"attack": {"card": selectedCard, "target": []}})} className="bubble">Perform</span>
          </div>
        </>
        )
    }
  return (
    <>
    <div className="activateInformation">
      <span className="bubbleMain">Attack</span>
      <span className="bubble">Cannot Attack</span>
    </div>
    </>
  )
  }
}

function StatInformation({selectedCard, selectedCardLocation, clickHandler}) {
  if (selectedCard.type !== "trap" && selectedCard.type !== "spell") {
    return (
      <>
        <div className="statInformation">
          <span className="bubbleMain">Type</span>
          <span className="bubble">{selectedCard.card_type}</span>
          <span className="bubbleMain">Attribute</span>
          <span className="bubble">{selectedCard.attribute}</span>
          <span className="bubbleMain">Typing</span>
          <span className="bubble">{selectedCard.monster_type}</span>
        </div>
        <div className="statInformation">
          {selectedCard.type === "monster" && 
            <>
              <span className="bubbleMain">Level</span>
              <span className="bubble">{selectedCard.level}</span>
            </>
          }
          {selectedCard.type === "xyz_monster" && 
            <>
              <span className="bubbleMain">Rank</span>
              <span className="bubble">{selectedCard.rank}</span>
            </>
          }
          {selectedCard.type === "link_monster" && 
            <>
              <span className="bubbleMain">Link Arrows</span>
              <span className="bubble">{selectedCard.link_arrows}</span>
            </>
          }
          <span title="Attack" className="bubbleMain">ATK</span>
          <span className="bubble">{selectedCard.attack}</span>
          {selectedCard.type !== "link_monster" && 
            <>
              <span title="Defense" className="bubbleMain">DEF</span>
              <span className="bubble">{selectedCard.defense}</span>
            </>
          }
          {selectedCard.type === "link_monster" && 
            <>
              <span className="bubbleMain">Link Rating</span>
              <span className="bubble">{selectedCard.link_rating}</span>
            </>
          }
          
        </div>
      </>
    )
  } else {
    return (
      <>
        <div className="statInformation">
          <span className="bubbleMain">Type</span>
          <span className="bubble">{selectedCard.card_type}</span>
          <span className="bubbleMain">Typing</span>
          <span className="bubble">{selectedCard.other_type}</span>
        </div>
      </>
    )
  }
}

function Card({card, cardLocation, className, clickHandler, dragHandler, dragStartHandler}) {
  if (card === undefined) {
    return <div></div>
  }
  const imagePath = `./images/${card.id}.jpg`;

  function cardJson() {
    return {"select": [card, cardLocation]};
  }
  
  return (
    <>
      
      {card.position !== "set" && <img draggable="true" onDragStart={(e) => dragStartHandler([card, cardLocation])} 
      onDrag={(e) => dragHandler()} onClick={() => clickHandler(cardJson())} className={`smallCard ${className} ${card.position === "defense" ? "defenseCard" : ""} 
      ${(cardLocation.includes("p2") && (cardLocation.includes("MM") || cardLocation.includes("ST") || cardLocation.includes("EM"))) ? "player2Card" : ""}`} 
      src={require(`${imagePath}`)} alt="card"></img>}

      {(card.position === "set" && card.type !== "spell" && card.type !== "trap") && <img draggable="true" onDragStart={(e) => dragStartHandler([card, cardLocation])} 
      onDrag={(e) => dragHandler()} onClick={() => clickHandler(cardJson())} className={`smallCard defenseCard ${className}`}
      src={require("./images/back.jpg")} alt="card"></img>}

      {(card.position === "set" && (card.type === "spell" || card.type === "trap")) && <img draggable="true" onDragStart={(e) => dragStartHandler([card, cardLocation])} 
      onDrag={(e) => dragHandler()} onClick={() => clickHandler(cardJson())} className={`smallCard ${className}`}
      src={require("./images/back.jpg")} alt="card"></img>}
    </>
  )
}

function LeftPanel({selectedCard, selectedCardLocation, clickHandler, summonableCards, activatableCards, attackers, settableCards}) {
  return (
    <>
      <div className="panel leftPanel">
        <CardPreview selectedCard={selectedCard}></CardPreview>
        <CardEffect selectedCard={selectedCard}></CardEffect>
        <CardInformation clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation}></CardInformation>
        <CardActions clickHandler={clickHandler} selectedCard={selectedCard} selectedCardLocation={selectedCardLocation} 
        summonableCards={summonableCards} activatableCards={activatableCards} attackers={attackers}
        settableCards={settableCards}></CardActions>
      </div>
    </>
  )
}

function ViewArea({clickHandler, dragHandler, dragStartHandler, selectedLocationCards, selectedLocationName}) {
  const [cards, setCards] = useState([]);

  useEffect(() => {
    if (selectedLocationCards !== null) {
      setCards(selectedLocationCards);
    }
  }, [selectedLocationCards]);

  if (cards === []) {
    return (
      <fieldset className="panelSection">
        <legend className="boxTitle">View Area</legend>
        <div className="viewAreaContainer">
          <input className="searchbar" type="text"></input>
          <div className="viewArea">
          </div>
        </div>
      </fieldset>
    )
  }
    
  const listCards = cards.map((element, index) => {
    return (
      <Card key={index} cardLocation={selectedLocationName} clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} className="viewAreaCard" card={element}></Card>
    )
  })

  return (
    <fieldset className="panelSection">
      <legend className="boxTitle">View Area</legend>
      <div className="viewAreaContainer">
        <input className="searchbar" type="text"></input>
        <div className="viewArea">
          {listCards}
        </div>
      </div>
    </fieldset>
  )
}

function PhaseInformation({clickHandler, currentPhase}) {
  return (
    <div className="phaseInformation">
      <span className="bubbleMain">Phase</span>
      <h3 onClick={() => clickHandler({"phase": "Draw Phase"})} title="Draw Phase" className={`phase ${currentPhase !== "Draw Phase" ? "deselected" : ""}`}>DP</h3>
      <h3 onClick={() => clickHandler({"phase": "Standby Phase"})} title="Standby Phase"  className={`phase ${currentPhase !== "Standby Phase" ? "deselected" : ""}`}>ST</h3>
      <h3 onClick={() => clickHandler({"phase": "Main Phase 1"})} title="Main Phase 1"  className={`phase ${currentPhase !== "Main Phase 1" ? "deselected" : ""}`}>M1</h3>
      <h3 onClick={() => clickHandler({"phase": "Battle Phase"})} title="Battle Phase"  className={`phase ${currentPhase !== "Battle Phase" ? "deselected" : ""}`}>BP</h3>
      <h3 onClick={() => clickHandler({"phase": "Main Phase 2"})} title="Main Phase 2" className={`phase ${currentPhase !== "Main Phase 2" ? "deselected" : ""}`}>M2</h3>
      <h3 onClick={() => clickHandler({"phase": "End Phase"})} title="End Phase" className={`phase ${currentPhase !== "End Phase" ? "deselected" : ""}`}>ED</h3>
      <h3 onClick={() => clickHandler({"phase": "Next Turn"})} title="Next Turn" className="phase">(Next Turn)</h3>
    </div>
  )
}

function PlayerInformation({playerName, playerInformation}) {
  return (
    <>
      <div className="playerInformationHalf">
        <div className="playerInformation">
          <span className="bubbleMain">{playerName}</span>
        </div>
        <div className="playerInformation">
          <span title="Life Points" className="bubbleMain">LP</span>
          <span className="bubble">{playerInformation.lp}</span>
        </div>
        <div className="playerInformation">
          <span className="bubbleMain">Normal Summons</span>
          <span className="bubble">{playerInformation.normal_summon_count}</span>
        </div>
      </div>
    </>
  )
}

function GameInformation({currentGameState, clickHandler}) {
  if (!currentGameState.players) {
    return (
      <>
      <fieldset className="panelSection gameInformationContainer">
        <legend className="boxTitle">Game Information</legend>
      </fieldset>
      </>
    )
  }
  return (
    <>
      <fieldset className="panelSection gameInformationContainer">
        <legend className="boxTitle">Game Information</legend>
        <div className="gameInformation">
          <span className="bubbleMain">Turn</span>
          <span className="bubble">{currentGameState.turn}</span>
          <span className="bubbleMain">Turn Player</span>
          <span className="bubble">{`Player ${currentGameState.turn_player}`}</span>
        </div>
        <PhaseInformation currentPhase={currentGameState.phase} clickHandler={clickHandler}></PhaseInformation>
      </fieldset>
    </>
  )
}

function PlayerInformationContainer({currentGameState, clickHandler}) {
  if (!currentGameState.players) {
    return (
    <fieldset className="panelSection playerInformationContainer">
      <legend className="boxTitle">Player Information</legend>
    </fieldset>
    )
  }
  const player1 = currentGameState.players[0];
  const player2 = currentGameState.players[1];
  return (
    <>
      <fieldset className="panelSection playerInformationContainer">
        <legend className="boxTitle">Player Information</legend>
        <div className="playerInformationSplit">
          <PlayerInformation playerName="Player 1" playerInformation={player1}></PlayerInformation>
          <PlayerInformation playerName="Player 2" playerInformation={player2}></PlayerInformation>
        </div>
      </fieldset>
    </>
  )
}

function RightPanel({currentGameState, clickHandler, dragHandler, dragStartHandler, selectedLocationCards, selectedLocationName}) {
  return (
    <>
      <div className="panel rightPanel">
        <GameInformation currentGameState={currentGameState} clickHandler={clickHandler}></GameInformation>
        <PlayerInformationContainer currentGameState={currentGameState} clickHandler={clickHandler}></PlayerInformationContainer>
        <ViewArea selectedLocationName={selectedLocationName} dragStartHandler={dragStartHandler} clickHandler={clickHandler} dragHandler={dragHandler} selectedLocationCards={selectedLocationCards}></ViewArea> 
        <div className="panelSection cardSearch"></div>
      </div>
    </>
  )
}

function Hand({clickHandler, dragHandler, dragStartHandler, dropHandler, handCards, handLocation}) {
  const [isDraggingOver, setDraggingOver] = useState(false);
  const [cards, setCards] = useState([]);

  useEffect(() => {
    if (handCards !== null) {
      setCards(handCards);
    }
  }, [handCards]);

  if (cards === []) {
    return (
      <div className="hand">
      </div>
    )
  }

  function handleDragOver(e) {
    e.preventDefault();
    setDraggingOver(true);
  }

  function handleDragLeave() {
    setDraggingOver(false);
  }

  function handleDrop(func){
    setDraggingOver(false);
    return func
  }

  const listCards = cards.map((element ,index) => {
    return (
      <Card key={index} cardLocation={handLocation} clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} className="handCard" card={element}></Card>
    )
  })

  return (
    <>
    {isDraggingOver && <div onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} onDrop={(e) => handleDrop(dropHandler(handLocation))} className="handContainer handDragging">
      {listCards}
    </div>}
    {!isDraggingOver && <div onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} onDrop={(e) => handleDrop(dropHandler(handLocation))} className="handContainer">
      {listCards}
    </div>}
    </>
  )
}

function Location({className, dropHandler, cards, locationClickHandler, locationName}) {
  const [isDraggingOver, setDraggingOver] = useState(false);

  function count() {
    return cards.length;
  }

  function handleDragOver(e) {
    e.preventDefault();
    setDraggingOver(true);
  }

  function handleDragLeave() {
    setDraggingOver(false);
  }

  function handleDrop(func){
    setDraggingOver(false);
    return func
  }

  return (
    <div onClick={(e) => locationClickHandler([cards, locationName])} onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} 
    onDrop={(e) => handleDrop(dropHandler(locationName))} className="locationContainer">
      {isDraggingOver && <div className={`location ${className} locationDrag`}></div>}
      {!isDraggingOver && <div className={`location ${className} ${className}`}></div>}
      <div className="locationCount">{count()}</div>
    </div>
  )
}

function EmptyZone({className, locationName, dropHandler}) {
  const [isDraggingOver, setDraggingOver] = useState(false);

  function handleDragOver(e) {
    e.preventDefault();
    setDraggingOver(true);
  }

  function handleDragLeave() {
    setDraggingOver(false);
  }

  function handleDrop(func){
    setDraggingOver(false);
    return func
  }

  if (className === "monsterZone") {
      return (
        <div onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} onDrop={() => dropHandler(handleDrop(locationName))} className="monsterDefenseZone">
          <div className="defenseZone"></div>
          {isDraggingOver && <div className={`zone monsterZone locationDrag`}></div>}
          {!isDraggingOver && <div className="zone monsterZone"></div>}
        </div>
      )
    } else if (className === "extraMonsterZone")
    return (
      <div onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} onDrop={() => dropHandler(handleDrop(locationName))} className="monsterDefenseZone">
        <div className="defenseZone"></div>
        {isDraggingOver && <div className={`zone extraMonsterZone locationDrag`}></div>}
        {!isDraggingOver && <div className="zone extraMonsterZone"></div>}
      </div>
    )
  return (
    <>
      <div onDragOver={(e) => handleDragOver(e)} onDragLeave={() => handleDragLeave()} onDrop={(e) => dropHandler(handleDrop(locationName))}>
        {isDraggingOver && <div className={`zone ${className} locationDrag`}></div>}
        {!isDraggingOver && <div className={`zone ${className}`}></div>}
      </div>
    </>
  )
}

function Zone({className, card, dragStartHandler, dragHandler, clickHandler, locationName, dropHandler}) {
  if (card === undefined || Object.keys(card).length === 0) {
    return (
      <EmptyZone dropHandler={dropHandler} locationName={locationName} className={className}/>
    )
  }

  if (className === "monsterZone") {
    return (
      <div className="monsterDefenseZone">
        <div className="defenseZone"></div>
        <div className="zone monsterZone"></div>
        <Card cardLocation={locationName} clickHandler={clickHandler} dragStartHandler={dragStartHandler} dragHandler={dragHandler} card={card}></Card>
      </div>
    )
  } else if (className === "extraMonsterZone")
    return (
      <div className="monsterDefenseZone">
        <div className="defenseZone"></div>
        <div className="zone extraMonsterZone"></div>
        <Card cardLocation={locationName} clickHandler={clickHandler} dragStartHandler={dragStartHandler} dragHandler={dragHandler} card={card}></Card>
      </div>
    )
  return (
    <>
      <div className="zoneContainer">
        <div className={`zone ${className}`}></div>
        <Card cardLocation={locationName} clickHandler={clickHandler} dragStartHandler={dragStartHandler} dragHandler={dragHandler} card={card}></Card>
      </div>
    </>
  )
}

function Field({currentGameState, clickHandler, dropHandler, dragStartHandler, locationClickHandler, dragHandler}) {
  const p1Field = currentGameState.fields[0];
  const p2Field = currentGameState.fields[1];
  const p1Hand = currentGameState.hands[0];
  const p2Hand = currentGameState.hands[1];
  return (
    <>
    <div className="container">
      <div></div>
      <div className="field">
        <Hand clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} handCards={p2Hand} handLocation={"p2H"}></Hand>
        <div className="zones">
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="deckZone" locationName={"p2D"} cards={p2Field.deck}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p2STZ5"} card={p2Field.spell_trap_zones[4]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p2STZ4"} card={p2Field.spell_trap_zones[3]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p2STZ3"} card={p2Field.spell_trap_zones[2]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p2STZ2"} card={p2Field.spell_trap_zones[1]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p2STZ1"} card={p2Field.spell_trap_zones[0]}/>
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="extraDeckZone" cards={p2Field.extra_deck} locationName={"p2ED"} />
        </div>
        <div className="zones">
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="graveyardZone" cards={p2Field.graveyard} locationName={"p2GY"} />
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p2MMZ5"} card={p2Field.monster_zones[4]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p2MMZ4"} card={p2Field.monster_zones[3]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p2MMZ3"} card={p2Field.monster_zones[2]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p2MMZ2"} card={p2Field.monster_zones[1]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p2MMZ1"} card={p2Field.monster_zones[0]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="fieldZone" locationName={"p2FZ"} card={p2Field.field_zone}/>
        </div>

        <div className="zones">
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="banishedZone" locationName={"p2BZ"} cards={p2Field.banished}/>
          <div className="emptySpace"></div>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="extraMonsterZone" locationName={"EMZ1"} 
          card={currentGameState.extra_monster_zones[0]}/>
          <div className="emptySpace"></div>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="extraMonsterZone" locationName={"EMZ2"} 
          card={currentGameState.extra_monster_zones[1]}/>
          <div className="emptySpace"></div>
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="banishedZone" locationName={"p1BZ"} cards={p1Field.banished}/>
        </div>

        <div className="zones">
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="fieldZone" locationName={"p1FZ"} card={p1Field.field_zone}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p1MMZ1"} card={p1Field.monster_zones[0]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p1MMZ2"} card={p1Field.monster_zones[1]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p1MMZ3"} card={p1Field.monster_zones[2]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p1MMZ4"} card={p1Field.monster_zones[3]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="monsterZone" locationName={"p1MMZ5"} card={p1Field.monster_zones[4]}/>
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="graveyardZone" locationName={"p1GY"} cards={p1Field.graveyard}/>
        </div>
        <div className="zones">
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="extraDeckZone" locationName={"p1ED"} cards={p1Field.extra_deck} />
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p1STZ1"} card={p1Field.spell_trap_zones[0]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p1STZ2"} card={p1Field.spell_trap_zones[1]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p1STZ3"} card={p1Field.spell_trap_zones[2]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p1STZ4"} card={p1Field.spell_trap_zones[3]}/>
          <Zone clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="spellTrapZone" locationName={"p1STZ5"} card={p1Field.spell_trap_zones[4]}/>
          <Location locationClickHandler={locationClickHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} className="deckZone" locationName={"p1D"} cards={p1Field.deck}/>
        </div>
        <Hand clickHandler={clickHandler} dragHandler={dragHandler} dragStartHandler={dragStartHandler} dropHandler={dropHandler} handCards={p1Hand} handLocation={"p1H"}></Hand>
      </div>
      <div></div>
    </div>
    </>
  );
}


export default function App() {
  const [showPopup, setShowPopup] = useState(false);
  const [choices, setChoices] = useState([]);
  const [choiceName, setChoiceName] = useState(null);
  let confirmedChoices = [];
  const [dragStartCard, setDragStartCard] = useState(null);
  const [dragStartLocation, setDragStartLocation] = useState(null);
  const [selectedLocationCards, setSelectedLocationCards] = useState([]);
  const [selectedLocationName, setSelectedLocationName] = useState(null);
  const [selectedCard, setSelectedCard] = useState({"id": "back", "desc": "Select a card"});
  const [selectedCardLocation, setSelectedCardLocation] = useState(null);
  const [currentGameState, setCurrentGameState] = useState({"hands": [[], []],
"extra_monster_zones": [{}, {}],
"fields": [{
  banished: [],
  deck: [],
  extra_deck: [],
  field_zone: {},
  graveyard: [],
  monster_zones: [{}, {}, {}, {}, {}],
  player: "1",
  spell_trap_zones:[{}, {}, {}, {}, {}]},
  {banished: [],
  deck: [],
  extra_deck: [],
  field_zone: {},
  graveyard: [],
  monster_zones: [{}, {}, {}, {}, {}],
  player: "2",
  spell_trap_zones: [{}, {}, {}, {}, {}],
  summonable: []}]});

  useEffect(() => {
    fetch("/api").then(response => {
      if (response.ok) {
        return response.json()
      }
    }).then(data => setCurrentGameState(data))
  }, []);

  const handleRequest = (data) => {
    return fetch("/api/request", {
      method: 'POST',
      body: JSON.stringify({
        content:data
      })
    }).then(response => response.json())
    .then(message => message);
  };

  function handleLocationClick(data) {
    setSelectedLocationCards(data[0]);
    setSelectedLocationName(data[1]);
  }

  function handleCardClick(info) {
    if (info.hasOwnProperty("select")) {
      setSelectedCard(info["select"][0]);
      setSelectedCardLocation(info["select"][1]);


      // Changing a cards position from the left panel
    } else if (info.hasOwnProperty("position")) {
      if (info["position"][0] === selectedCard.position) {
        return;
      }
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["201"] !== "error") {
            setCurrentGameState(message["201"]);
            selectedCard.position = info["position"][0];
          }
        }
      });
      
    // Changing the phase from the right panel
    } else if (info.hasOwnProperty("phase")) {
      if (info["phase"][0] === currentGameState.phase) {
        return;
      }
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["201"] !== "error") {
            setCurrentGameState(message["201"]);
          }
        }
      });

    // Normal / Tribute Summon
    } else if (info.hasOwnProperty("perform_summon")) {
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler);
          }
        }
          
      });
    } else if (info.hasOwnProperty("extra_summon")) {
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler);
          }
        }
          
      });
    } else if (info.hasOwnProperty("activate")) {
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler);
          } else {
            setCurrentGameState(message["201"]);
          }
        }
      });
    } else if (info.hasOwnProperty("set")) {
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler)
          } else {
            setCurrentGameState(message["201"]);
          }
        }
      });

    } else if (info.hasOwnProperty("attack")) {
      handleRequest(info)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler);
          }
        }
      });
    }
  }

  function choiceClickHandler(data, count=-1) {
    var send = data;
    if (count >= 0) {
      confirmedChoices.push(data);
      send = confirmedChoices;
    }
    
    setShowPopup(false);
    setChoices([]);
    setChoiceName(null);
    handleRequest(send)
      .then(message => {
        if (message["201"]) {
          if (message["data"]["choice"]) {
            showChoices(message["data"]["choice"], choiceClickHandler);
          } else {
            setCurrentGameState(message["201"]);
            confirmedChoices = [];
          }
        }
      });
  }

  function showChoices(choices, choiceClickHandler) {
    if (choices["zones"]) {
      choices = choices["zones"];
      const choiceList = choices.map((choice) => (
        <>
          {choice.includes("MM") && (
            <span key={choice} onClick={() => choiceClickHandler({"choice": choice})} className="choice">{`Main Monster Zone ${choice.substring(5, 6)}`}</span>
          )}
      
          {choice.includes("EM") && (
            <span key={choice} onClick={() => choiceClickHandler({"choice": choice})} className="choice">{`Extra Monster Zone ${choice.substring(3, 4)}`}</span>
          )}

          {choice.includes("ST") && (
            <span key={choice} onClick={() => choiceClickHandler({"choice": choice})} className="choice">{`Spell/Trap Zone  ${choice.substring(5, 6)}`}</span>
          )}
        </>
      ));
      setChoiceName("Zones");
      setChoices(choiceList);
      setShowPopup(true);;

    } else if (choices["material"]) {
      const count = choices["count"];
      choices = choices["material"];
      const choiceList = choices.map((choice) => (
        <img alt="choice" src={require(`./images/${choice["id"]}.jpg`)} key={choice} onClick={() => choiceClickHandler({"choice": choice}, count)} className="choiceImage"></img>
      ));
      setChoiceName("Material");
        setChoices(choiceList);
        setShowPopup(true);;

    } else if (choices["target"]) {
      choices = choices["target"];
      const choiceList = choices.map((choice) => (
        <>
          {choice["player"] && <img alt="choice" src={require("./images/player.jpg")} key={choice} onClick={() => choiceClickHandler({"choice": choice})} className="choiceImage"></img>}
          {!choice["player"] && <img alt="choice" src={require(`./images/${choice["id"]}.jpg`)} key={choice} onClick={() => choiceClickHandler({"choice": choice})} className="choiceImage"></img>}
        </>
      ));
      setChoiceName("Target");
      setChoices(choiceList);
      setShowPopup(true);;
    } else if (choices["action"]) {
      setCurrentGameState(choices["game"]);
      const count = choices["count"];
      choices = choices["action"];
      const choiceList = choices.map((choice) => (
        <img alt="choice" src={require(`./images/${choice["data"]["id"]}.jpg`)} key={choice} onClick={() => choiceClickHandler({"action_choice": choice["data"]}, count)} className="choiceImage"></img>
      ));
      setChoiceName("Activate");
      setChoices(choiceList);
      setShowPopup(true);;
    } else if (choices["chain"]) {
        setCurrentGameState(choices["game"]);
        choices = choices["chain"];
        const choiceList = choices.map((choice) => (
          <>
            {choice["end"] && <img alt="choice" src={require("./images/nochain.jpg")} key={choice} 
            onClick={() => choiceClickHandler({"chain_choice": "end"})} className="choiceImage"></img>}
            
            {!choice["end"] && <img alt="choice" src={require(`./images/${choice["data"]["id"]}.jpg`)} key={choice} 
            onClick={() => choiceClickHandler({"chain_choice": choice["data"]})} className="choiceImage"></img>}
          </>
      ));
      setChoiceName("Chain");
      setChoices(choiceList);
      setShowPopup(true);;
    }
  
  }

  function handleDragStart(data) {
    setDragStartCard(data[0]);
    setDragStartLocation(data[1]);
  }

  function handleDrag() {
    return;
  }

  function handleDrop(locationName) {
    handleRequest({"move": {"origin":[dragStartLocation, dragStartCard],
    "target": locationName}})
    .then(message => {
      if (message["201"]) {
        if (message["201"] !== "error") {
          setCurrentGameState(message["201"]);
          if (locationName === selectedLocationName || dragStartLocation === selectedLocationName) {
            const newCards = [...selectedLocationCards];
            newCards.splice(dragStartCard.index, 1);
            setSelectedLocationCards(newCards);
          }
          
          if (dragStartCard.id === selectedCard.id && dragStartLocation === selectedCardLocation) {
            if (dragStartCard.index) {
              if (dragStartCard.index === selectedCard.index) {
                setSelectedCard(message["data"]);
                setSelectedCardLocation(locationName);
              }
            } else{
              setSelectedCard(message["data"]);
              setSelectedCardLocation(locationName);
            }
          }
        }
      }
    });
  }


  return (
    <div className="container">
      <LeftPanel clickHandler={handleCardClick} selectedCard={selectedCard} 
      selectedCardLocation={selectedCardLocation} summonableCards={currentGameState["summonable"]} 
      activatableCards={currentGameState["activatable"]} attackers={currentGameState["attackers"]}
      settableCards={currentGameState["settable"]}/>

      <Field currentGameState={currentGameState} dragStartHandler={handleDragStart} dropHandler={handleDrop} dragHandler={handleDrag} clickHandler={handleCardClick} locationClickHandler={handleLocationClick}/>
      <RightPanel currentGameState={currentGameState} clickHandler={handleCardClick} dragStartHandler={handleDragStart} dropHandler={handleDrop} dragHandler={handleDrag} 
      selectedLocationName={selectedLocationName} selectedLocationCards={selectedLocationCards}/>
      {showPopup && 
      <>
        <div className="choiceBox">
          <div className="choiceTitle">{choiceName}</div>
          <div className="choiceContainer">{choices}</div>
        </div>
      </>
      }
    </div>
  )
}
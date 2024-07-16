import React, {useState} from 'react';
import './Inventory.css';
import {ToggleButton} from "./Button";

function Inventory({inventoryData} : {inventoryData: any}) {
    const [chosenTabs, setChosenTabs] = useState<string[]>(Object.keys(inventoryData))

    const clickTab = (tab: string) => {
        if (!chosenTabs.includes(tab)) {
            setChosenTabs([...chosenTabs, tab])
        } else {
            setChosenTabs(chosenTabs.filter((t) => t !== tab))
        }
    }

    const getItems = () => {
        let items: any[] = []
        for (let tab of chosenTabs) {
            for (let item of inventoryData[tab]) {
                items.push({tab: tab, name: item})
            }
        }
        return items
    }

    return (
        <div className="InventoryContainer">
            <div className="InventoryTabs">
                {Object.keys(inventoryData).map((tabName: any) => {
                    return <ToggleButton text={tabName} func={() => clickTab(tabName)} active={chosenTabs.includes(tabName)} key={tabName} />
                })}
            </div>
            <div className="InventoryItems">
                {getItems().map((item, index) => {
                    return (
                        <div key={index} className="InventoryItem">
                            <div className="InventoryItemName">
                                {item.name}
                            </div>
                            <div className="InventoryItemTab">
                                {item.tab}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    );
}

export default Inventory;
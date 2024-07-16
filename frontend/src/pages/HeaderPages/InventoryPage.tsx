import React from 'react';
import Inventory from "../../components/Inventory";
import './InventoryPage.css';

export default function InventoryPage({data} : {data: any}) {
    return (
        <div className="InventoryPage">
            <div className="InventoryTitle">Inventory</div>
            <div className="InventoryCoins">
                Coins: {data.coins}
            </div>
            <Inventory inventoryData={data.inventory}/>
        </div>
    );
}
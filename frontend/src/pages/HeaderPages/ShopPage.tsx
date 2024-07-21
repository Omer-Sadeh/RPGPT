import React, {useEffect, useState} from "react";
import {motion} from "framer-motion";
import API from "../../services/API";
import Button, {BigButton} from "../../components/Button";
import './ShopPage.css';
import ImageLoader from "../../components/ImageLoader";
import AUTH from "../../services/auth";

function ShopItem({item, category, price, func} : {item: string, category: string, price: number, func: any}) {
    const [errorMessage, setErrorMessage] = useState('');

    const handleFunc = async () => {
        const error = await func(item);
        setErrorMessage(error);
        // sleep for 1 second
        await new Promise(r => setTimeout(r, 1000));
        setErrorMessage('');
    }

    return (
        <motion.div key={item} className={errorMessage ? "ShopItem shopItemErrored" : "ShopItem"} onClick={handleFunc}
                    initial={{ opacity: 0.5, x: 0}}
                    animate={errorMessage ? { x: [0, 5, -5, 0]} : {}}
                    transition={errorMessage ? { times: [0, 0.1, 0.9, 1] } : {}}
                    whileHover={{ scale: 1.03, opacity: 1 }}>
            {errorMessage ? <div className="ShopItemError">{errorMessage}</div> : <>
                <div className="ShopItemName">{item}</div>
                <div className="ShopItemCategory">[{category}]</div>
                <div className="ShopItemPrice">{price}$</div></>}
        </motion.div>
    );
}

function ShopPage({saveData, saveName, img}: { saveData: any, saveName: string, img: string }) {
    const [mode, setMode] = useState("main");

    const getShop = async () => {
        await API.shop(AUTH.getToken(), saveName).then();
    }

    const chooseItem = async (item: string, mode: "buy" | "sell") => {
        return await API.shopAction(AUTH.getToken(), saveName, mode, item).then(() => {
            return '';
        }).catch((error: any) => {
            return error.message;
        });
    }

    const renderShopItems = (itemDict: any, chooseFunc: any) => {
        if (Object.keys(itemDict).length === 0) {
            return (<div className="ShopText">Nothing to {mode === "buy" ? "sell to" : "buy from"} You!</div>);
        }
        return (
            <div className="ShopItems">
                {Object.keys(itemDict).map((item, index) => {
                    return <ShopItem key={index} item={item} category={itemDict[item][0]} price={itemDict[item][1]} func={chooseFunc} />
                })}
            </div>
        );
    }

    const renderShopMenu = () => {
        if (mode === "main") {
            return (
                <div className="ShopMenu">
                    {Object.keys(saveData.shop.sold_items).length > 0 && <BigButton text={"Buy"} func={() => setMode("buy")} />}
                    <div className="button-div" />
                    {Object.keys(saveData.shop.buy_items).length > 0 && <BigButton text={"Sell"} func={() => setMode("sell")} />}
                </div>
            );
        } else if (mode === "buy") {
            return renderShopItems(saveData.shop.sold_items, (item: string) => chooseItem(item, "buy"));
        } else if (mode === "sell") {
            return renderShopItems(saveData.shop.buy_items, (item: string) => chooseItem(item, "sell"));
        } else return null;
    }

    return (
        <div className="ShopContainer">
            <h1>Shop <span className="ShopGold">
                [ {saveData.coins} Gold ]
            </span></h1>
            {(typeof saveData.shop === 'string') ? "Searching for a shop around..." : (Object.keys(saveData.shop).length === 0 ? <Button text={"Look for a shop"} func={getShop} /> :
                <div className="ShopContent">
                    <ImageLoader bytes={img} alt={"shopImage"} className={"ShopkeeperImage"} />
                    <div className="ShopkeeperName">{saveData.shop.shopkeeper_description}:</div>
                    <div className="ShopkeeperDialogue">"{saveData.shop.shopkeeper_recommendation}"</div>
                    {renderShopMenu()}
                    <div className="button-div"/>
                    {mode !== "main" && <BigButton text={"Back"} func={() => setMode("main")}/>}
                </div>)}
        </div>
    );
}

export default ShopPage;
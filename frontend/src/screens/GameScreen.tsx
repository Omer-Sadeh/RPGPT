import React, {useEffect, useState} from 'react';
import { doc, onSnapshot } from "firebase/firestore";
import AUTH from "../services/auth";
import API from "../services/API";
import './GameScreen.css';
import Header from "../components/Header";
import SavesList from "../pages/SavesList";
import GamePage from "../pages/GamePage";
import Screen from "./Screen";
import {LoadingScreen} from "./MessageScreen";
import OverCard from "../components/OverCard";
import InventoryPage from "../pages/HeaderPages/InventoryPage";
import SkillsPage from "../pages/HeaderPages/SkillsPage";
import ProfilePage from "../pages/HeaderPages/ProfilePage";
import ShopPage from "../pages/HeaderPages/ShopPage";
import QuestsPage from "../pages/HeaderPages/QuestsPage";
import NewSave from "../pages/NewSave";
import { IoMdContact } from "react-icons/io";
import { GiSchoolBag } from "react-icons/gi";
import { HiMiniChartBarSquare } from "react-icons/hi2";
import { AiFillShop } from "react-icons/ai";
import { FaBookmark } from "react-icons/fa6";
import {db} from "../firebase";

function GameScreen() {
    const logout = () => {
        handleCard('');
        AUTH.ResetAuth();
    }

    const [status, setStatus] = useState("loading");
    const [saves, setSaves] = useState<any>({});
    const [card, setCard] = useState('');
    const handleCard = (newCard: string) => {
        if (card === newCard) setCard('');
        else setCard(newCard);
    }
    const [fullUserData, setFullUserData] = useState<any>({});
    const [currentSave, setCurrentSave] = useState('');
    const [sceneImg, setSceneImg] = useState("");
    const [shopImg, setShopImg] = useState({img: "", key: ""});
    const [characterImg, setCharacterImg] = useState({img: "", key: ""});

    useEffect(() => {
        if (!AUTH.check()) {
            logout();
        }
        getSaves().then(() => {
            setStatus("up");
        });
        onSnapshot(doc(db, "users", AUTH.getName()), (doc: any) => {
            if (!doc.exists()) {
                logout();
            } else setFullUserData(doc.data());
        });
        // eslint-disable-next-line
    }, []);

    useEffect(() => {
        updateCharacterImg().then();
        updateSceneImg().then();
        updateShopImg().then();
        // eslint-disable-next-line
    }, [fullUserData, currentSave]);

    const updateSceneImg = async () => {
        if (currentSave === '') return;
        await API.getImage(AUTH.getToken(), currentSave, 'scene').then((res) => {
            setSceneImg(res);
        }).catch((error) => {
            console.error(error.message);
        });
    }

    const updateShopImg = async () => {
        if (currentSave === '') return;
        if (shopImg.key !== fullUserData[currentSave].shop.shopkeeper_description) {
            await API.getImage(AUTH.getToken(), currentSave, 'shop').then((res) => {
                setShopImg({img: res, key: fullUserData[currentSave].shop.shopkeeper_description});
            }).catch((error) => {
                setShopImg({img: "", key: fullUserData[currentSave].shop.shopkeeper_description});
            });
        }
    }

    const updateCharacterImg = async () => {
        if (currentSave === '') return;
        if (characterImg.key !== fullUserData[currentSave].background.name) {
            await API.getImage(AUTH.getToken(), currentSave, 'character').then((res) => {
                setCharacterImg({img: res, key: fullUserData[currentSave].background.name});
            }).catch((error) => {
                setCharacterImg({img: "", key: fullUserData[currentSave].background.name});
            });
        }
    }

    const getSaves = async () => {
        let saves = await API.getSaves(AUTH.getToken()).catch((error) => {
            console.warn("Error getting saves: " + error.message);
            logout();
        });
        if (saves) {
            setSaves(saves);
        }
    }

    const newSaveScreen = () => {
        if (status === "newSave") setStatus("up");
        else setStatus("newSave");
    };

    const newSave = async (theme: string, background: any) => {
        setStatus("loading");
        await API.newSave(AUTH.getToken(), theme, background).catch((error) => {
            console.error("Error creating new save: " + error.message);
            setStatus("up");
        });
        getSaves().then(() => setStatus("up"));
    }

    const loadSave = async (save: string) => {
        setStatus("loading");
        let saveData = await API.loadSave(AUTH.getToken(), save).catch((error) => {
            console.error("Error loading save: " + error.message);
            setStatus("up");
        });
        if (saveData) {
            setCurrentSave(save);
            setStatus("up");
        }
    }

    const unloadSave = () => {
        handleCard('');
        setCurrentSave('');
    }

    const deleteSave = async (save: string) => {
        setStatus("loading")
        await API.deleteSave(AUTH.getToken(), save).catch((error) => {
            console.log("Error deleting save: " + error.message);
        });
        setStatus("up");
        getSaves().then();
    }

    const endSave = () => {
        let save = currentSave;
        unloadSave();
        deleteSave(save).then();
    }

    const generateCards = () => {
        if (currentSave === '') return [];
        return [
            {name: 'profile', icon: <IoMdContact />, activation: () => handleCard('profile'), component: <ProfilePage data={fullUserData[currentSave]} img={characterImg.img}/>},
            {name: 'inventory', icon: <GiSchoolBag />, activation: () => handleCard('inventory'), component: <InventoryPage data={fullUserData[currentSave]}/>},
            {name: 'skills', icon: <HiMiniChartBarSquare />, activation: () => handleCard('skills'),
                component: <SkillsPage saveData={fullUserData[currentSave]} save_name={currentSave} />,
                notif: fullUserData[currentSave].action_points > 0},
            {name: 'shop', icon: <AiFillShop />, activation: () => handleCard('shop'), component: <ShopPage saveData={fullUserData[currentSave]} saveName={currentSave} img={shopImg.img}/>},
            {name: 'quests', icon: <FaBookmark />, activation: () => handleCard('quests'), component: <QuestsPage saveData={fullUserData[currentSave]} />}
        ];
    }

    return (
        <div className="gameScreen">
            <Header username={AUTH.getName()} data={{name: currentSave, data: fullUserData[currentSave]}} cards={generateCards()} unload={unloadSave} logout={logout} />
            {generateCards().map((Card, index) => {
                return <OverCard show={card === Card.name} hideFunc={() => setCard('')} key={index}>{Card.component}</OverCard>;
            })}

            <div className="gameScreenContent">
                <Screen isMounted={status === "loading"}>
                    <LoadingScreen/>
                </Screen>

                <Screen isMounted={status !== "loading" && currentSave !== ''}>
                    <GamePage save={currentSave} data={fullUserData[currentSave]} sceneImg={sceneImg} endGame={endSave} />
                </Screen>

                <Screen isMounted={status !== "loading" && status !== "newSave" && currentSave === ''}>
                    <SavesList saves={saves} loadSave={loadSave} newSave={newSaveScreen} deleteSave={deleteSave} />
                </Screen>

                <Screen isMounted={status !== "loading" && status === "newSave" && currentSave === ''}>
                    <NewSave func={newSave} cancel={newSaveScreen} />
                </Screen>
            </div>
        </div>
    );
}

export default GameScreen;
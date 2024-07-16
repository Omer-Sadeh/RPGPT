import React, {useEffect} from 'react';
import Button, {BigButton, BigButtonActived} from "../components/Button";
import "./NewSave.css";
import API from "../services/API";
import FadeScreen from "../components/FadeScreen";
import {FillableFilteredValuesGrid, UnlabeledClickableValuesGrid} from "../components/ValuesGrid";

const getThemeCover = (theme: string) => {
    try {
        require(`../../public/media/posters/${theme}.jpg`);
        return `./media/posters/${theme}.jpg`;
    } catch (e) {
        return "./media/posters/default.jpg";
    }
}

function ThemesPage({themes, choose, show} : {themes: string[], choose: (theme: string) => void, show: boolean}) {
    return (
        <FadeScreen show={show} classname="themesGrid">
            {themes.map((theme) => {
                return (
                    <div key={theme} className="themeItem" onClick={() => choose(theme)}>
                        <img src={getThemeCover(theme)} className="themeImage" alt={theme} />
                        <div className="themeName">{theme}</div>
                    </div>
                );
            })}
        </FadeScreen>);
}

function InputPage({theme, show, clear, submit} : {theme: any, show: boolean, clear: any, submit: any}) {
    const [answers, setAnswers] = React.useState<any>({});
    const [shown, setShown] = React.useState<string>("");

    useEffect(() => {
        if (show) {
            let answers: any = {};
            Object.keys(theme.fields).forEach((field: any) => {
                answers[field] = "";
            });
            setAnswers(answers);
        }
        // eslint-disable-next-line
    }, [show]);

    const isReady = () => {
        let ready = true;
        Object.keys(answers).forEach((field) => {
            if (answers[field] === "") {
                ready = false;
            }
        });
        return ready;
    }

    const setAnswer = (field: string, answer: string) => {
        let newAnswers = {...answers};
        newAnswers[field] = answer;
        setAnswers(newAnswers);
    }

    function SetupAnswer({show, answer, options, set}: {show: boolean, answer: string, options: string[] | string, set: any, clear: any}) {
        const [text, setText] = React.useState<string>(answer);

        const renderOptions = () => {
            if (typeof options === "string") {
                return (
                    <div className="setupTextInput">
                        <input type="text" className="setupInput" value={text} placeholder={options}
                               onChange={(e) => setText(e.target.value)}/>
                        <BigButton text={"Set"} func={() => set(text)}/>
                    </div>
                );
            } else {
                return <UnlabeledClickableValuesGrid values={options} onClick={set} />;
            }
        }

        return <FadeScreen show={show} classname="setupFieldOptions">{renderOptions()}</FadeScreen>;
    }

    return (<FadeScreen show={show} classname="inputContainer">
            <img src={getThemeCover(theme.name)} className="inputImage" alt={theme.name}/>

            <div className="currentSetup">
                <FillableFilteredValuesGrid values={answers} filteredOut={["details"]} onClick={setShown}/>
                {Object.keys(answers).filter((field) => field !== "details").map((field) => {
                    return <SetupAnswer key={field} show={shown === field} answer={answers[field]} options={theme.fields[field]}
                                        set={(answer: string) => {
                                            setAnswer(field, answer);
                                            setShown("");
                                        }}
                                        clear={() => setAnswer(field, "")}/>;
                })}
            </div>

            <input type="text" className="setupInput" value={answers["details"] ? answers["details"] : ""}
                   placeholder={"Write a short description of your character..."}
                   onChange={(e) => setAnswer("details", e.target.value)}/>

            <BigButtonActived text={"Create!"} func={() => submit(theme.name, answers)} active={isReady()}/>
    </FadeScreen>
);
}

function NewSave({
    func, cancel}: { func: any, cancel: () => void}) {
    const [loading, setLoading] = React.useState<boolean>(true);
    const [themes, setThemes] = React.useState<any>({});
    const [selectedTheme, setSelectedTheme] = React.useState<string>("");

    useEffect(() => {
        API.getThemesData().then((data) => {
            setThemes(data);
            setLoading(false);
        }).catch((e) => {
            console.error("Error loading themes data:", e.message);
            cancel();
        });
    }, [cancel]);

    const selectTheme = (theme: string) => {
        setSelectedTheme(theme);
    }

    if (loading) {
        return <div>Loading...</div>;
    }
    return (
        <div className="newSaveContainer">
            <div className="newSaveTitle">Create Your Character:</div>
            <div className="newSaveContent">
                <ThemesPage themes={Object.keys(themes)} choose={selectTheme} show={!selectedTheme}/>
                <InputPage theme={selectedTheme ? themes[selectedTheme] : themes["fantasy"]}
                           show={selectedTheme !== ""}
                           clear={() => selectTheme("")}
                            submit={func}
                />
            </div>
            <div className="newSaveFooter">
                <Button text={"cancel"} func={cancel} />
            </div>
        </div>
    );
}

export default NewSave;
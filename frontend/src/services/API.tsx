import {req} from './Requests';

class API {
    static async login(username: string, password: string) {
        return await req('login', '', {}, {
          username: username,
          password: password
      });
    }

    static async register(username: string, password: string) {
        return await req('register', '', {}, {
            username: username,
            password: password
        });
    }

    static async systemStatus() {
        return await req('startup', '', {}, {});
    }

    static async getSaves(auth: string) {
        return await req('saves_list', auth, {}, {});
    }

    static async getThemesData() {
        return await req('themes', '', {}, {});
    }

    static async newSave(auth: string, theme: string, background: any) {
        return await req('new_save', auth, {
            theme: theme
        }, {
            background: background
        });
    }

    static async loadSave(auth: string, save: string) {
        return await req('load', auth, {
            save_name: save
        }, {});
    }

    static async deleteSave(auth: string, save: string) {
        return await req('delete', auth, {
            save_name: save
        }, {});
    }

    static async spendSkill(auth: string, skill: string, save: string) {
        return await req('spend', auth, {
            skill: skill,
            save_name: save
        }, {});
    }

    static async goals(auth: string, save: string, regen: boolean) {
        return await req('goals', auth, {
            save_name: save,
            regen: regen
        }, {});

    }

    static async newStory(auth: string, save: string, goal: string) {
        return await req('new_story', auth, {
            save_name: save,
            goal: goal
        }, {});
    }

    static async shop(auth: string, save: string) {
        return await req('shop', auth, {
            save_name: save
        }, {});
    }

    static async shopAction(auth: string, save: string, action: "buy" | "sell", item: string) {
        if (action === 'buy') {
            return await req('buy', auth, {
                save_name: save,
                item_name: item
            }, {});
        } else {
            return await req('sell', auth, {
                save_name: save,
                item_name: item
            }, {});
        }
    }

    static async advance(auth: string, save: string, action: string) {
        return await req('advance', auth, {
            save_name: save,
            action: action
        }, {});
    }

    static async newOption(auth: string, save: string, new_action: string) {
        return await req('new_option', auth, {
            save_name: save,
            new_action: new_action
        }, {});
    }

    static async endGame(auth: string, save: string) {
        return await req('end_story', auth, {
            save_name: save
        }, {});
    }

    static async getImage(auth: string, save: string, category: string) {
        return await req('image', auth, {
            save_name: save,
            category: category
        }, {});
    }
}

export default API;
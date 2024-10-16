import obswebsocket
from obswebsocket import obsws, requests
from poke2d import get_pokemon_2d
import poke2d
import os
import obs_info

ws = obsws(obs_info.host, obs_info.port, obs_info.password)
ws.connect()

class OBS_Manager:
    def __init__(self):
        self.auctioner_pokemon = dict()
        self.auctioner_id = dict()
        self.curr_img = ''
        self.auctioner_assigner = 0


    def set_defaults(self, empty):
        image_path = get_pokemon_2d('smeargle')

        if empty:
            image_path = ''

        for i in range(8):
            for j in range(1, 7):
                ws.call(requests.SetInputSettings(
                inputName="auctioner_" + str(i) + "_pk" + str(j),  # The name of your image source in OBS
                inputSettings={"file": image_path}  # The new image path
            ))
                
        for i in range(8):
            ws.call(requests.SetInputSettings(
            inputName='auctioner_' + str(i) + '_money',
            inputSettings={
                "text": '$30000',
            }
        ))
            ws.call(requests.SetInputSettings(
            inputName='auctioner_' + str(i),
            inputSettings={
                "text": 'name' + str(i),
            }
        ))
            
        ws.call(requests.SetInputSettings(
            inputName="current_bid" ,  # The name of your image source in OBS
            inputSettings={"text": 'None'}  # The new image path
        ))

        #changing previous bid field
        ws.call(requests.SetInputSettings(
            inputName="previous_bid" ,  # The name of your image source in OBS
            inputSettings={"text": 'None'}  # The new image path
        ))

        ws.call(requests.SetInputSettings(
            inputName="auction_pokemon" ,  # The name of your image source in OBS
            inputSettings={"file": ''}  # The new image path
        ))

        ws.call(requests.SetInputSettings(
            inputName='current_auction_pokemon_text',
            inputSettings={
                "text": 'None',
            }
        ))
                

    def set_current_pokemon_auction_info(self, pokemon_name:str):
        image_path = get_pokemon_2d(pokemon_name)
        self.curr_img = image_path

        ws.call(requests.SetInputSettings(
            inputName="auction_pokemon" ,  # The name of your image source in OBS
            inputSettings={"file": image_path}  # The new image path
        ))

        ws.call(requests.SetInputSettings(
            inputName='current_auction_pokemon_text',
            inputSettings={
                "text": pokemon_name.title(),
            }
        ))

    def set_bidding_info(self, new_amt, new_bidder, old_amt, old_bidder, start):
        #current_bid field
        new_info_str = '$' + str(new_amt) + ' - ' + new_bidder.title()

        old_info_str = 'None'
        #previous_bid field
        if not start:
            old_info_str = '$' + str(old_amt) + ' - ' + old_bidder.title()


        #changing current bids
        ws.call(requests.SetInputSettings(
            inputName="current_bid" ,  # The name of your image source in OBS
            inputSettings={"text": new_info_str}  # The new image path
        ))

        #changing previous bid field
        ws.call(requests.SetInputSettings(
            inputName="previous_bid" ,  # The name of your image source in OBS
            inputSettings={"text": old_info_str}  # The new image path
        ))

    def set_party_pokemon(self, pokemon_img, user, party_no):
        ws.call(requests.SetInputSettings(
            inputName="auctioner_" + str(user) + "_pk" + str(party_no) ,  # The name of your image source in OBS
            inputSettings={"file": pokemon_img}  # The new image path
        ))

    def set_auctioner_name(self, username):
        number = self.auctioner_id[username]

        ws.call(requests.SetInputSettings(
            inputName='auctioner_' + str(number) ,  # The name of your image source in OBS
            inputSettings={"text": username}  # The new image path
        ))

    def set_auctioner_money(self, amount, username):
        number = self.auctioner_id[username]

        ws.call(requests.SetInputSettings(
            inputName='auctioner_' + str(number) + '_money' ,  # The name of your image source in OBS
            inputSettings={"text": "$" + str(amount)}  # The new image path
        ))

    def empty_fields(self):
        ws.call(requests.SetInputSettings(
            inputName="current_bid" ,  # The name of your image source in OBS
            inputSettings={"text": ''}  # The new image path
        ))

        #changing previous bid field
        ws.call(requests.SetInputSettings(
            inputName="previous_bid" ,  # The name of your image source in OBS
            inputSettings={"text": ''}  # The new image path
        ))

        ws.call(requests.SetInputSettings(
            inputName="auction_pokemon" ,  # The name of your image source in OBS
            inputSettings={"file": ''}  # The new image path
        ))

        ws.call(requests.SetInputSettings(
            inputName='current_auction_pokemon_text',
            inputSettings={
                "text": '',
            }
        ))

# obs_manager.set_current_pokemon_auction_info("dialga")
# obs_manager.set_bidding_info(10000, 'peter jenkins', 5000, 'somebodyelse')
# obs_manager.set_party_pokemon('https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/132.png', 3, 6)
#obs_manager.set_defaults(True)

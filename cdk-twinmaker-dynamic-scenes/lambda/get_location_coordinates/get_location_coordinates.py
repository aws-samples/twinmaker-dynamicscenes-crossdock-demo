import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def calc_slot_position(slot_id):
    # inbound_slot_6 as example for row var
    # split row by underscore into an array
    slots = range(1,9)
    slot1_positions = { "inbound" : 5, "sorting" : 120, "outbound" : 240 }
    try:
        slot_parts = slot_id.split('_')
        if int(slot_parts[2]) in slots:
            slot_multiplier = int(slot_parts[2]) * 10
            return slot1_positions[slot_parts[0]] + slot_multiplier
        else:
            return 0
    except:
        return 0

def calc_row_position(row_id):
    rows = range(1,6)
    base_coord = -14
    row = row_id.split('_')[1]
    # row has number and an alpha character, so split by alpha character and get the first element
    if int(row[0]) in rows:
        coord = base_coord + (int(row[0]) * 25)
        if row[1] == "b":
            coord = coord + 12
        return coord
    else:
        return 12

def lambda_handler(event, context):
    try:
        # get the grid_ref from the event
        grid_ref = event['body']['grid_ref']
        output = event['body']
        # split grid_ref by the '-' character
        grid_ref_parts = grid_ref.split('-')
        slot = calc_slot_position(grid_ref_parts[0])
        logging.info(slot)
        row = calc_row_position(grid_ref_parts[1])
        logging.info(row)

        output['loc_x'] = slot
        output['loc_y'] = row
        
        return {
            'statusCode': 200,
            'body': output
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'grid_ref not found in event'
        }

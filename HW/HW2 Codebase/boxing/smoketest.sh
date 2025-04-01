#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
    case $1 in
        --echo-json) ECHO_JSON=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
    echo "Checking health status..."
    curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Service is healthy."
    else
        echo "Health check failed."
        exit 1
    fi
}

#Function to check the database connectio
check_db(){
    echo "Checking database connection..."
    curl -s -X GET "$BASE_URL/db-check" | grep -q '"status: "success"'
    if [ $? -eq 0 ]; then
        echo "Database connection is healthy."
    else
        echo "Database check failed."
        exit 1
    fi
}


##########################################################
#
# Boxer Management
#
##########################################################

create_boxer(){
    name=$1
    weight=$2
    heigh=$3
    reach=$4
    age=$5

    echo "Adding boxer ($name - $weight, $height) to the ring..."
    curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
        -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"height\":$height, \"reach\":\"$reach\", \"age\":$age}" | grep -q '"status": "success"' 
    
    if [ $? -eq 0 ]; then
        echo "Boxer added successfully."
    else
        echo "Failed to add boxer."
        exit 1
    fi
}

delete_boxer_by_id(){
    boxer_id=$1

    echo "Deleting boxer by ID ($boxer_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "boxer deleted successfully by ID ($boxer_id)."
    else
        echo "Failed to delete song by ID ($boxer_id)."
        exit 1
    fi
}

get_leaderboard(){
    echo "Getting the leaderboards by boxer..."
    response=$(curl -s -X GET "$BASE_URL/boxer-leaderboard?sort=win_count")
    if echo "$respone" | grep -q '"status": "success"'; then
        echo "Boxer leaderboard retrieved successfuly."
        if ["$ECHO_JSON" = true]; then
            echo "Leaderboard JSON (sorted by win)"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get boxer leaderboard."
        exit 1
    fi
}

get_boxer_by_id(){
    boxer_id=$1

    echo "Getting song by ID ($boxer_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-from-catalog-by-id/$boxer_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer retrieved successfully by ID ($boxer_id)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Boxer JSON (ID $boxer_id):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get Boxer by ID ($boxer_id)."
        exit 1
    fi
}

get_boxer_by_name(){
    boxer_name=$1

    echo "Getting song by ID ($boxer_name)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-from-catalog-by-name/$boxer_name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer retrieved successfully by Name ($boxer_name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Boxer JSON (Name $boxer_name):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get Boxer by name ($boxer_name)."
        exit 1
    fi
}

get_weight_class(){
    boxer_weight=$1

    echo "Getting weight class of boxer ($boxerweight)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-from-catalog-by-name/$boxer_weight")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer retrieved successfully by weight_class ($boxer_weight)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Boxer JSON (Weight $boxer_weight):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get Boxer by weight ($boxer_weight)."
        exit 1
    fi
}


############################################################
#
# Play ring
#
############################################################

fight(){
    echo "Simulating a fight..."
    response=$(curl -s -X GET "$BASE_URL/fight")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer fight retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "$response" | jq .
        fi
    else
        echo "Failed to simulate fight"
        exit 1
    fi
}

clear_ring() {
    echo "Clearing ring..."
    response=$(curl -s -X POST "$BASE_URL/clear-ring")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Ring cleared successfully."
    else
        echo "Failed to clear ring."
        exit 1
    fi
}

enter_ring() {
    Boxer=$1

    echo "Adding song to playlist: $Boxer..."
    response=$(curl -s -X POST "$BASE_URL/add-boxer-to-ring" \
        -H "Content-Type: application/json" \
        -d "{\"boxer\":\"$Boxer\"")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer added to ring successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Song JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to add Boxer to ring."
        exit 1
    fi
}

get_boxers(){
    echo "Retrieving all songs from playlist..."
    response=$(curl -s -X GET "$BASE_URL/get-all-boxers-from-ring")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "All boxers retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Songs JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve all boxers from ring."
        exit 1
    fi
}

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

#Healthy checks
check_health
check_db

# Create Boxers 
create_boxer "James" 133 56 23 18
create_boxer "Ali" 230 70 40 24
create_boxer "Canelo" 218 69 9 30
create_boxer "John" 190 34 20 25
create_boxer "Rock" 250 79 50 40

delete_boxer_by_id 1

get_leaderboard

get_boxer_by_id 2
get_boxer_by_name "Canelo"

get_weight_class 135

fight
clear_ring

enter_ring "Ali"
get_boxers

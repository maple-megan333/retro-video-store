from app import db
from app.models.video import Video
from app.models.rental import Rental
from app.models.customer import Customer
from app.routes.rental_routes import query_rentals
from flask import Blueprint, jsonify, abort, make_response, request
from app.routes.helper_functions import validate_model, custom_query

videos_bp = Blueprint("videos_bp", __name__, url_prefix="/videos")

@videos_bp.route("", methods=["GET"])
def get_all_video():
    videos = custom_query(Video, ['id','title','release_date'])
    videos_response = []
    for video in videos:
        videos_response.append(video.to_dict())
    return jsonify(videos_response)

@videos_bp.route("/<video_id>", methods=["GET"])
def get_one_video_by_id(video_id):
    video = validate_model(Video, video_id)
    return video.to_dict()

@videos_bp.route("", methods=["POST"])
def create_a_video():
    request_body = request.get_json()
    try:
        new_video = Video.from_dict(request_body)
    except KeyError as key_error:
        abort(make_response({"details":f"Request body must include {key_error.args[0]}."}, 400))
    db.session.add(new_video)
    db.session.commit()

    return make_response(new_video.to_dict(), 201)

@videos_bp.route("/<video_id>", methods=["PUT"])
def update_a_video(video_id):
    video = validate_model(Video, video_id)
    request_body = request.get_json()
    try:
        video.title = request_body["title"]
        video.release_date = request_body["release_date"]
        video.total_inventory = request_body["total_inventory"]
    except KeyError as key_error:
        abort(make_response({"details":f"Request body must include {key_error.args[0]}."}, 400))
    
    db.session.add(video)
    db.session.commit()

    return make_response(video.to_dict(), 200)

@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_a_video(video_id):
    video = validate_model(Video, video_id)

    db.session.delete(video)
    db.session.commit()

    return make_response(jsonify(video.to_dict()), 200)

@videos_bp.route("/<video_id>/rentals", methods=["GET"])
def get_rentals_by_video(video_id):
    video = validate_model(Video, video_id)
    query = custom_query(Rental,['id','name','postal_code'],{"video_id":video.id, "status": Rental.RentalStatus.CHECKOUT})

    response = []
    for rental in query:
        customer = validate_model(Customer, rental.customer_id)
        rental_info =  customer.to_dict()
        rental_info["due_date"] = rental.due_date
        response.append(rental_info)
    return jsonify(response)


@videos_bp.route("/<video_id>/history", methods=["GET"])
def get_customer_had_been_checked_out_video(video_id):
    video = validate_model(Video, video_id)
    query = custom_query(Rental,['id','name','postal_code'],{"video_id":video.id, "status": Rental.RentalStatus.CHECKIN})

    response = []
    for rental in query:
        customer = validate_model(Customer, rental.customer_id)
        rental_info =  customer.to_dict()
        rental_info["checkout_date"] = rental.checkout_date
        rental_info["due_date"] = rental.due_date
        response.append(rental_info)
    return jsonify(response)


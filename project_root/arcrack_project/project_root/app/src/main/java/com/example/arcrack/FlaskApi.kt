package com.example.armeasureapp

import retrofit2.Call
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.POST

interface FlaskApi {
    @FormUrlEncoded
    @POST("/upload")
    fun sendMeasurement(
        @Field("image") image: String,
        @Field("distance") distance: Float
    ): Call<String>
}

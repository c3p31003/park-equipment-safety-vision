package com.example.arcrack

import retrofit2.Call
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.POST

interface ApiService {
    @FormUrlEncoded
    @POST("/receive_length")
    fun sendLength(
        @Field("length") length: Double
    ): Call<Map<String, String>>
}

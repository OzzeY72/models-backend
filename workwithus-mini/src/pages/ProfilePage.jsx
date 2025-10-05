import { useEffect, useState } from "react";
import "swiper/css";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";

const BASE_URL = import.meta.env.VITE_API_URL;

export default function ProfilePage({ id }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        let url = "";

        if (user.user_type === "escort") {
          url = `${BASE_URL}/masters/${id}`;
        } else if (user.user_type === "agency") {
          url = `${BASE_URL}/agencies/${id}`;
        } else {
          throw new Error("Unknown user type");
        }

        const res = await fetch(url);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  if (loading) return <p>Loading...</p>;
  if (!data) return <p>Error loading profile</p>;

  return (
    <div className="container mx-auto p-4 max-w-md text-center">
      <h2 className="text-xl font-semibold mb-4">{data.name}</h2>

      {data.photos && data.photos.length > 0 ? (
        <Swiper
          modules={[Pagination]}
          loop={false}
          centeredSlides={true}
          slidesPerView={1.2}
          spaceBetween={12}
          pagination={{ clickable: true }}
        >
          {data.photos.map((p) => (
            <SwiperSlide key={p}>
              <img
                src={`${BASE_URL}/static/${p}`}
                alt="photo"
                className="w-full h-64 object-cover rounded-lg"
              />
            </SwiperSlide>
          ))}
        </Swiper>
      ) : (
        <p>No photos available</p>
      )}

      <div className="mt-4 text-left space-y-2">
        <p>
          <strong>Phone:</strong> {data.phone}
        </p>
        <p>
          <strong>Address:</strong> {data.address}
        </p>
        {data.is_agency !== undefined && (
          <p>
            <strong>Is Agency:</strong> {data.is_agency ? "Yes" : "No"}
          </p>
        )}
        {data.model_count !== undefined && (
          <p>
            <strong>Model count:</strong> {data.model_count}
          </p>
        )}
      </div>
    </div>
  );
}

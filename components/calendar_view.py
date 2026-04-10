for week in cal_matrix:
    cols = st.columns(7)

    for i, day in enumerate(week):

        if day == 0:
            cols[i].write("")
            continue

        curr_dt = date(cv.year, cv.month, day)
        hst = (curr_dt - tgl_tanam).days
        idx = min(max(0, day-1), len(forecast_30)-1)

        label = label_singkat(
            rbs_singkong_final(forecast_30[idx], hst)
        )

        bg, border = get_color(label)

        key = f"day_{cv.month}_{day}"

        with cols[i]:

            # =========================
            # OVERLAY CONTAINER
            # =========================
            st.markdown(f"""
            <div style="
                position:relative;
                height:105px;
                border-radius:12px;
                overflow:hidden;
            ">

                <!-- BOX WARNA (LAYER BAWAH) -->
                <div style="
                    position:absolute;
                    inset:0;
                    background:{bg};
                    border:2px solid {border};
                    border-radius:12px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:20px;
                    font-weight:bold;
                    z-index:1;
                ">
                    {day}
                </div>

                <!-- BUTTON OVERLAY (LAYER ATAS) -->
                <form action="" method="post">
                    <button name="clicked_day" value="{day}" style="
                        position:absolute;
                        inset:0;
                        width:100%;
                        height:100%;
                        background:transparent;
                        border:none;
                        cursor:pointer;
                        z-index:2;
                    "></button>
                </form>

            </div>
            """, unsafe_allow_html=True)

            # =========================
            # HANDLE CLICK (STREAMLIT)
            # =========================
            if st.button(" ", key=key, use_container_width=True):
                selected_day = day

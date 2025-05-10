#trendAnalysis main.trendAnalysis
@main.route('/trend_analysis', methods=['GET', 'POST'])
def trend_analysis():
    form = TrendAnalysisForm()
    logging.debug(f"Form data: {form.data}")
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        trend_time_scale = form.trend_time_scale.data
        trend_analysis_type= form.trend_analysis_type.data
        user_id = form.user_id.data
        session_id = form.session_id.data
        aspect_based = ""

        logging.debug("Form TrendAnalysis data: ", {
            "start_date": start_date,
            "end_date": end_date,
            "trend_time_scale": trend_time_scale,
            "user_id": user_id,
            "session_id": session_id,
            "trend_analysis_type":trend_analysis_type

        })

        try:
            validate_date_range(start_date, end_date)
            logging.debug("Date range validated")
        except ValueError as e:
            flash(str(e), 'danger')
            logging.error(f"Date range validation failed: {e}")
            return redirect(url_for('main.trend_analysis'))


        if trend_analysis_type == "generic":
                # Fetch and group the messages
                messages = fetch_messages(start_date, end_date, user_id, session_id, aspect_based)
                period_groups = time_series_aggregation(messages, trend_time_scale)
                trend_data = create_trend_data(period_groups, trend_time_scale)

        elif trend_analysis_type == "chat_messages":
                input= fetch(input_data)
                # to be completed here....

        elif trend_analysis_type == "aspect_based":
                input= fetch(input_data)
                # to be completed here....
    
        # Skip invalid sentiment data
        valid_trend_data = []
        for entry in trend_data:
            if 'all_scores' in entry.get('sentiment_scores', {}):
                valid_trend_data.append(entry)
            else:
                logging.warning(f"Skipping invalid sentiment_scores structure for entry: {entry}")

        # Generate and save the sentiment and emotion plots
        fig_sentiment = plot_sentiment(valid_trend_data)  # Assuming plot_sentiment returns a figure
        if fig_sentiment is None:
            logging.error("Failed to generate sentiment plot")
            flash("Error generating sentiment plot", 'danger')
            return redirect(url_for('main.trend_analysis'))

        # Save the plots as images in the static folder
        static_folder = os.path.join(current_app.root_path, 'static')  # Path to the static folder
        plot_path = os.path.join(static_folder, 'sentiment_plot.png')
        fig_sentiment.savefig(plot_path)

        # Pass the plot image paths to the template
        return render_template('results_trend_analysis.html', trend_data=valid_trend_data, 
                               sentiment_plot_url=url_for('static', filename='sentiment_plot.png'))

    return render_template('trendanalysis.html', form=form)